import os
from flask import Flask, render_template, request, redirect, url_for, session, abort, jsonify
from database import *
from encription import *
from werkzeug.utils import secure_filename
import os
from flask import send_from_directory
from flask_cors import CORS
import database as db

# Use the repository's web/html folder as the template folder
template_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'web', 'html'))
app = Flask(__name__, template_folder=template_dir)

CORS(app)

# Simple secret for sessions (change in production)
app.secret_key = os.environ.get('FLASK_SECRET', 'dev-secret-key-change-me')
app.config.update(
                SESSION_COOKIE_HTTPONLY=True,
                SESSION_COOKIE_SAMESITE='Lax')

@app.route('/')
def index():
    return redirect(url_for('login'))

#SESSION MANAGEMENT
#login page & authentication
@app.route('/login', methods=['GET', 'POST'])
def login():
    # GET -> render login page
    if request.method == 'GET':
        return render_template('login.html')

    # POST -> authenticate
    user = request.form.get('username') or request.args.get('username')
    password = request.form.get('password') or request.args.get('password')

    if not db.check_params([user, password]):
        abort(400)

    res = db.get_users(user)
    if not res:
        # user not found
        abort(401)

    stored_hash = res[0]['pass']
    if check_password(password, stored_hash):
        session['user'] = user
        session['privilege'] = res[0].get('privilege', 0)
        return redirect(url_for('dashboard'))
    else:
        abort(401)

# Logout endpoint
@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

#check login decorator
def login_required(f):
    from functools import wraps

    @wraps(f)
    def wrapped(*args, **kwargs):
        if 'user' not in session:
            return redirect(url_for('login'))
        return f(*args, **kwargs)

    return wrapped





# Static file serving
@app.route('/css/<path:filename>')
def css(filename):
    css_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'web', 'css'))
    return send_from_directory(css_dir, filename)

@app.route('/img/<path:filename>')
def img(filename):
    img_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'web', 'resources'))
    return send_from_directory(img_dir, filename)

# Autocomplete endpoint for client names
@app.route('/data', methods=['GET'])
@login_required
def data():
    q = request.args.get('data', '')
    if db.check_params([q]) is False:
        return jsonify([])
    clients = db.check_clients(q)
    if not clients:
        return jsonify([])
    return jsonify(clients)

@app.route('/pdf/<filename>')
@login_required
def serve_pdf(filename):
    files_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'files', 'bills'))
    return send_from_directory(files_dir, filename)

# API requests
# API: return users list for management UI
@app.route('/api/users', methods=['GET'])
@login_required
def api_users():
    try:
        results = db.get_users('*')
        # normalize list of dicts -> return only username and optional fields
        out = []
        for r in results:
            if isinstance(r, dict):
                out.append({'user': r.get('user') or r.get('name')})
            else:
                out.append({'user': r})
        return jsonify(out)
    except Exception:
        return jsonify([])
    
# API: invoices listing
@app.route('/api/invoices', methods=['GET'])
@login_required
def api_invoices():
    client = request.args.get('client', '').strip()
    paid = request.args.get('paid', 'all')
    try:
        conn = db.connect()
        cur = conn.cursor(dictionary=True)
        base = "SELECT clientes.name as cliente, idfactura, ubicacion_factura, factura_pendiente, facturas.email FROM facturas INNER JOIN clientes ON facturas.cliente = clientes.idcliente"
        params = []
        where = []
        if client:
            where.append("clientes.name LIKE %s")
            params.append(client + '%')
        if paid == 'pending':
            where.append("factura_pendiente = %s")
            params.append(1)
        elif paid == 'paid':
            where.append("factura_pendiente = %s")
            params.append(0)
        if where:
            base = base + ' WHERE ' + ' AND '.join(where) + ';'
            print('Final query:', base, params)
        cur.execute(base, params)
        rows = cur.fetchall()
        cur.close()
        conn.close()
        return jsonify(rows)
    except Exception as e:
        print('api_invoices error:', e)
        return jsonify([])
    
# API: current user info
@app.route('/api/me', methods=['GET'])
@login_required
def api_me():
    return jsonify({
        'user': session.get('user'),
        'privilege': session.get('privilege', 0)
    })

#API: clients info
@app.route('/api/clients', methods=['GET'])
@login_required
def api_clients():
    client = request.args.get('name', '*')
    return jsonify(db.clients_info(client))

#API: contact info
@app.route('/api/contacts', methods=['GET'])
@login_required
def api_contact():
    id = request.args.get('client_id')
    if not id:
        return ("Missing id", 400)
    return jsonify(db.contact_info(id))

# API: addresses info
@app.route('/api/addresses', methods=['GET'])
@login_required
def api_addresses():
    client_id = request.args.get('client_id')
    if not client_id:
        return ("Missing client_id", 400)
    try:
        return jsonify(db.addresses_info(client_id))
    except Exception as e:
        print('api_addresses error:', e)
        return jsonify([])


# API: add contact for a client
@app.route('/api/contacts/add', methods=['POST'])
@login_required
def api_contact_add():
    client_id = request.form.get('client_id') or request.json and request.json.get('client_id')
    name = request.form.get('name') or request.json and request.json.get('name')
    email = request.form.get('email') or request.json and request.json.get('email')
    tel = request.form.get('tel') or request.json and request.json.get('tel')
    facturas = request.form.get('facturas')
    if not client_id or not name:
        return ("Missing parameters", 400)
    try:
        db.add_contact(client_id, name, email, tel, facturas)
        return ("Contact added", 201)
    except Exception as e:
        print('api_contact_add error:', e)
        return (f"Error adding contact: {e}", 500)


# API: add address for a client
@app.route('/api/addresses/add', methods=['POST'])
@login_required
def api_address_add():
    client_id = request.form.get('client_id') or request.json and request.json.get('client_id')
    direccion = request.form.get('direccion') or request.json and request.json.get('direccion')
    poblacion = request.form.get('poblacion') or request.json and request.json.get('poblacion')
    codigo_postal = request.form.get('codigo_postal') or request.json and request.json.get('codigo_postal')
    pais = request.form.get('pais') or request.json and request.json.get('pais')
    if not client_id or not direccion:
        return ("Missing parameters", 400)
    try:
        db.add_address(client_id, direccion, poblacion, codigo_postal, pais)
        return ("Address added", 201)
    except Exception as e:
        print('api_address_add error:', e)
        return (f"Error adding address: {e}", 500)

#USER MANAGEMENT
# Users edit (change password)
@app.route('/users/edit', methods=['GET', 'POST'])
@login_required
def users_edit():
    if request.method == 'GET':
        return render_template('users/users_edit.html')

    # POST -> update password
    username = request.form.get('username')
    password = request.form.get('password')
    if not username or not password:
        return ("Missing parameters", 400)
    if len(password) < 8:
        return ("Password too short", 400)
    try:
        hashed = encrypt_password(password)
        if isinstance(hashed, bytes):
            hashed = hashed.decode('utf-8')
        db.update_data("UPDATE users SET pass=%s WHERE user=%s", (hashed, username))
        return ("User updated", 200)
    except Exception as e:
        return (f"Error updating user: {e}", 500)


# Users delete
@app.route('/users/delete', methods=['GET', 'POST'])
@login_required
def users_delete():
    if request.method == 'GET':
        return render_template('users/users_delete.html')

    username = request.form.get('username')
    if not username:
        return ("Missing username", 400)
    try:
        db.delete_data("DELETE FROM users WHERE user = %s", (username,))
        return ("User deleted", 200)
    except Exception as e:
        return (f"Error deleting user: {e}", 500)

# Users add
@app.route('/users/add', methods=['GET', 'POST'])
def users():
    
    # Allow public POST so users can self-register.
    # For GET, require login to view the register module inside the dashboard;
    # if not logged in, redirect to login page.
    if request.method == 'GET':
        if db.privileges(session.get('user', '')) == 1:
            pass
        elif db.privileges(session.get('user', '')) == 0:
            abort(403)
        else:
            abort(403)
        if 'user' not in session:
            return redirect(url_for('login'))
        return render_template('users/user_add.html')

    # POST -> create user (public)
    user = request.form.get('username')
    password = request.form.get('password')
    privilege = request.form.get('privilege', 0)
    if not db.check_params([user, password]):
        abort(400)

    if db.check_username(user):
        return ("Username already exists", 409)

    hashed_password = encrypt_password(password)
    # store as utf-8 string in DB
    if isinstance(hashed_password, bytes):
        hashed_password = hashed_password.decode('utf-8')

    db.create_user(user, hashed_password, privilege)
    return ("User registered successfully", 201)



#INVOICE MANAGEMENT
# Invoices edit page & update
@app.route('/invoices/edit', methods=['GET', 'POST'])
@login_required
def invoices_edit():


# Clients edit page & update
    if request.method == 'GET':
        return render_template('facturas/invoices_edit.html')
    # POST -> update invoice
    id_ = request.form.get('id')
    cliente = request.form.get('cliente')
    email = request.form.get('email')
    factura_pendiente = request.form.get('factura_pendiente')
    if not id_:
        return ("Missing id", 400)
    try:
        conn = db.connect()
        cur = conn.cursor()
        cur.execute("UPDATE facturas SET cliente = (SELECT idcliente from clientes WHERE name = %s), email=%s, factura_pendiente=%s WHERE idfactura=%s", (cliente, email, factura_pendiente, id_))
        conn.commit()
        cur.close()
        conn.close()
        return ("Invoice updated", 200)
    except Exception as e:
        return (f"Error updating invoice: {e}", 500)

    try:
        conn = connect()
        cur = conn.cursor()
        cur.execute("SELECT name FROM clientes WHERE name LIKE %s LIMIT 20", (q + '%',))
        rows = cur.fetchall()
        cur.close()
        conn.close()
        # rows may be list of tuples
        names = [r[0] for r in rows]
        return jsonify(names)
    except Exception as e:
        return jsonify([])
    
# Upload endpoint for invoices
@app.route('/invoices/add', methods=["GET", 'POST'])
@login_required
def invoice():
    if request.method == 'GET':
        if 'user' not in session:
            return redirect(url_for('login'))
        return render_template('facturas/upload_fragment.html')
    # ensure upload folder exists under repo/files/bills
    upload_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'files', 'bills'))
    os.makedirs(upload_dir, exist_ok=True)

    file = request.files.get('file')
    client = request.form.get('client')
    email = request.form.get('email')
    checkbox = request.form.get('checkbox')

    if not file or file.filename == '':
        return ("No file uploaded", 400)

    if not client:
        return ("Client is required", 400)

    try:
        filename = secure_filename(file.filename)
        file_path = os.path.join(upload_dir, filename)
        file.save(file_path)

        # Insert into DB using database.connect() if available, else fallback
        try:
            db.upload_invoice(client, file_path, email, checkbox)
        except Exception as db_err:
            # remove file if DB insert failed
            try:
                os.remove(file_path)
            except Exception:
                pass
            return (f"Database error: {db_err}", 500)

        return ("File uploaded and data saved successfully!", 201)
    except Exception as e:
        return (f"Upload error: {e}", 500)
    
# Invoices delete page & delete
@app.route('/invoices/delete', methods=['GET', 'POST'])
@login_required
def invoices_delete():
    if request.method == 'GET':
        return render_template('facturas/invoices_delete.html')
    # POST -> delete invoice
    invoice_id = request.form.get('id')
    if not invoice_id:
        return ("ID is required", 400)
    try:
        db.delete_invoice(invoice_id)
        return ("Invoice deleted successfully", 200)
    except Exception as e:
        return (f"Error deleting invoice: {e}", 500)

# Dashboard handling
#DASHBOARD
@app.route('/dashboard')
@login_required
def dashboard():
    return render_template('dashboard.html')

# Menu endpoint
@app.route('/menu', methods=['GET'])
def menu():
    import json
    with open(os.path.join(template_dir, 'menu.json'), 'r', encoding='utf-8') as f:
        menu_data = json.load(f)
    q = request.args.get('user', '')
    user = session.get('user', '')
    if db.privileges(user) == 1:
        return jsonify(menu_data["admin"])
    elif db.privileges(user) == 0:
        return jsonify(menu_data["user"])
    return abort(403)

#CLIENT MANAGEMENT
@app.route('/clients', methods=['GET'])
@login_required
def clients():
    return render_template('clientes/clients_list.html')

#clients add page
@app.route('/clients/add', methods=['GET', 'POST'])
@login_required
def clients_add():
    if request.method == 'GET':
        return render_template('clientes/clients_add.html')
    # POST -> add client
    name = request.form.get('name')
    nif = request.form.get('nif')
    db.check_params([name, nif])
    if not name:
        return ("Missing name", 400)
    try:
        db.add_client(name, nif)
        return ("Client added", 201)
    except Exception as e:
        return (f"Error adding client: {e}", 500)



@app.route('/clients/edit', methods=['GET', 'POST'])
@login_required
def clients_edit_page():
    if request.method == 'GET':
        return render_template('clientes/clients_edit.html')
    client_id = request.form.get('id')
    name = request.form.get('name') 
    nif = request.form.get('nif')
    if not client_id or not name:
        return ("Missing parameters", 400)
    try:
        db.update_client(client_id, name, nif)
        return ("Client updated", 200)
    except Exception as e:
        print('clients_edit error:', e)
        return (f"Error updating client: {e}", 500)





if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=80)
