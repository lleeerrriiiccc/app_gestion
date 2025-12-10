import eventlet
eventlet.monkey_patch()
import os
from flask import Flask, render_template, request, redirect, url_for, session, abort, jsonify
import requests
from database import *
from encription import *
from werkzeug.utils import secure_filename
import os
from flask import send_from_directory
from flask_cors import CORS
import database as db
import files as files
import jwt, datetime
from flask_socketio import SocketIO, join_room, leave_room
import alerts as ntf
from concurrent.futures import ThreadPoolExecutor

executor = ThreadPoolExecutor(max_workers=4)

# Use the repository's web/html folder as the template folder
template_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'web', 'html'))
app = Flask(__name__, template_folder=template_dir)
socketio = SocketIO(app, cors_allowed_origins="*", async_mode='eventlet',
                    logger=True, engineio_logger=True)
CORS(app)
@socketio.on('connect')
def handle_connect():
    # Try to identify the user from the JWT cookie and join a room named after the username
    try:
        token = request.cookies.get('token')
        if token:
            payload = jwt.decode(token, app.config['SECRET_KEY'], algorithms=["HS256"])
            username = payload.get('username')
            if username:
                join_room(str(username))
                print(f"Socket connected and joined room: {username}")
            else:
                print('Socket connected (no username in token)')
        else:
            print('Socket connected (no token)')
    except Exception as e:
        print('Socket connect error decoding token:', e)


@socketio.on('disconnect')
def handle_disconnect():
    try:
        token = request.cookies.get('token')
        if token:
            payload = jwt.decode(token, app.config['SECRET_KEY'], algorithms=["HS256"])
            username = payload.get('username')
            if username:
                try:
                    leave_room(str(username))
                except Exception:
                    pass
                print(f"Socket disconnected from room: {username}")
            else:
                print('Socket disconnected (no username)')
        else:
            print('Socket disconnected (no token)')
    except Exception as e:
        print('Socket disconnect error:', e)


# Simple secret for sessions (change in production)
app.secret_key = os.environ.get('FLASK_SECRET', 'dev-secret-key-change-me')
app.config.update(
                SESSION_COOKIE_HTTPONLY=True,
                SESSION_COOKIE_SAMESITE='Lax')

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'GET':
        return redirect(url_for('login'))
def enviar_notificacion(usuario, mensaje):
    socketio.emit('notificacion', {
        'usuario': usuario,
        'mensaje': mensaje
    })

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
    print(res)
    if check_password(password, stored_hash):
        token = jwt.encode({
        "username": user,
        "role": res[0]['privilege'],
        "exp": datetime.datetime.now(tz=datetime.timezone.utc) + datetime.timedelta(hours=1)
        }, app.config["SECRET_KEY"])
        resp = redirect(url_for('dashboard'))
        resp.set_cookie("token", token, httponly=True, samesite="Strict")
        return resp
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
        token = request.cookies.get("token") 
        if not token:
            return redirect(url_for("login"))
        try:
            payload = jwt.decode(token, app.config["SECRET_KEY"], algorithms=["HS256"])
        except Exception:
            return redirect(url_for("login"))
        session['user'] = payload['username']
        session['privilege'] = payload['role']
        return f(*args, **kwargs)

    return wrapped

    return wrapped

def internal_required(f):
    from functools import wraps

    @wraps(f)
    def wrapped(*args, **kwargs):
        print('Request from IP:', request.remote_addr)
        if request.remote_addr == '10.94.255.191':  # Example internal IP
            return f(*args, **kwargs)
        return abort(403)
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
@app.route('/js/<path:filename>')
def js(filename):
    # Serve JS files publicly so that pages (including login) can load shared client scripts
    js_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'web', 'js'))
    return send_from_directory(js_dir, filename)

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

@app.route('/pdf/bills/<filename>')
@login_required
def serve_pdf(filename):
        files_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'files', 'bills'))
        return send_from_directory(files_dir, filename)

@app.route('/pdf/planos/piezas/<filename>')
@login_required
def serve_planos_piezas(filename):
        files_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'files', 'planos'))
        return send_from_directory(files_dir, filename)

@app.route('/pdf/planos/productos/<filename>')
@login_required
def serve_planos_productos(filename):
        files_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'files', 'planos'))
        return send_from_directory(files_dir, filename)

# API requests
# API: return users list for management UI
@app.route('/api/users', methods=['GET'])
@login_required
def api_users():
    if request.args.get('dept'):
        dept = int(request.args.get('dept'))
        try:
            results = db.get_users(dept=dept)
            return jsonify(results)
        except Exception:
            return jsonify([])
    try:
        results = db.get_users()
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
            params.append('%' + client + '%')
        if paid == 'pending':
            where.append("factura_pendiente = %s")
            params.append(1)
        elif paid == 'paid':
            where.append("factura_pendiente = %s")
            params.append(0)
        if where:
            base = base + ' WHERE ' + ' AND '.join(where) + ';'
        order_by = " ORDER BY idfactura ASC;"
        base = base + order_by
        cur.execute(base, params)
        rows = cur.fetchall()
        cur.close()
        conn.close()
        return jsonify(rows)
    except Exception as e:
        return jsonify([])

@app.route('/api/departments', methods=['GET'])
@internal_required
def api_departments():
    try:
        results = db.get_departments()
        return jsonify(results)
    except Exception:
        return jsonify([])

# API: current user info
@app.route('/api/me', methods=['GET'])
@login_required
def api_me():
    token = request.cookies.get("token")
    if not token:
        return jsonify({"logged": False}), 401

    try:
        data = jwt.decode(token, app.config["SECRET_KEY"], algorithms=["HS256"])
        print('Decoded token data:', data)
        return jsonify({
            "logged": True,
            "username": data["username"],
            "role": data["role"]
        })
    except:
        return jsonify({"logged": False}), 401

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


@app.route('/api/contacts/delete', methods=['POST'])
@login_required
def api_contact_delete():
    contact_id = request.form.get('id') or (request.json and request.json.get('id'))
    if not contact_id:
        return ("Missing id", 400)
    try:
        db.delete_contact(contact_id)
        return ("Contact deleted", 200)
    except Exception as e:
        print('api_contact_delete error:', e)
        return (f"Error deleting contact: {e}", 500)

@app.route('/api/contacts/update', methods=['POST'])
@login_required
def api_contact_update():
    id = request.json.get('id')
    client_id = request.json.get('client_id')
    name = request.json.get('name')
    email = request.json.get('email')
    tel = request.json.get('tel')
    facturas = request.json.get('facturas')
    try:
        db.update_contact(id, client_id, name, email, tel, facturas)
        return ("Contact updated", 200)
    except Exception as e:
        print('api_contact_update error:', e)
        return (f"Error updating contact: {e}", 500)


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


@app.route('/api/products', methods=['GET'])
@login_required
def api_products():
    q = request.args.get('q', '*')
    idproducto = request.args.get('id')
    try:
        prods = db.products_list(q, idproducto)
        return jsonify(prods)
    except Exception as e:
        print('api_products error:', e)
        return jsonify([])


@app.route('/api/pedido', methods=['GET'])
@login_required
def api_pedido():
    pedido_id = request.args.get('id')
    if not pedido_id:
        return ("Missing id", 400)
    try:
        data = db.get_pedido(pedido_id)
        lines = db.get_pedido_lines(pedido_id)
        id_direccion_envio = data.get('direccion_envio') if data else None
        direccion_envio = db.get_direccion_envio(id_direccion_envio) if id_direccion_envio else None
        return jsonify({'pedido': data, 'lines': lines, 'direccion_envio': direccion_envio})
    except Exception as e:
        print('api_pedido error:', e)
        return jsonify({})


@app.route('/api/pedidos/add_line', methods=['POST'])
@login_required
def api_pedidos_add_line():
    payload = request.get_json(silent=True)
    if not payload:
        return ("Missing JSON payload", 400)
    pedido_id = payload.get('pedido_id')
    producto = payload.get('producto') or payload.get('producto_id')
    cantidad = payload.get('cantidad', 1)
    if not pedido_id or not producto:
        return ("Missing parameters", 400)
    try:
        db.add_linea_pedido(pedido_id, producto, cantidad)
        return ("Line added", 201)
    except Exception as e:
        print('api_pedidos_add_line error:', e)
        return (f"Error: {e}", 500)


@app.route('/api/pedidos/update_address', methods=['POST'])
@login_required
def api_pedidos_update_address():
    payload = request.get_json(silent=True)
    if not payload:
        return ("Missing JSON payload", 400)
    pedido_id = payload.get('pedido_id')
    direccion = payload.get('direccion_envio')
    if not pedido_id or direccion is None:
        return ("Missing parameters", 400)
    try:
        db.update_pedido_address(pedido_id, direccion)
        return ("Address updated", 200)
    except Exception as e:
        print('api_pedidos_update_address error:', e)
        return (f"Error: {e}", 500)


@app.route('/api/addresses/delete', methods=['POST'])
@login_required
def api_address_delete():
    addr_id = request.form.get('id') or (request.json and request.json.get('id'))
    if not addr_id:
        return ("Missing id", 400)
    try:
        db.delete_address(addr_id)
        return ("Address deleted", 200)
    except Exception as e:
        print('api_address_delete error:', e)
        return (f"Error deleting address: {e}", 500)


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
    
@app.route('/api/addresses/update', methods=['POST'])
@login_required
def api_address_update():
    id = request.json.get('id')
    client_id = request.json.get('client_id')
    direccion = request.json.get('direccion')
    poblacion = request.json.get('poblacion')
    codigo_postal = request.json.get('codigo_postal')
    pais = request.json.get('pais')
    try:
        db.update_address(id, client_id, direccion, poblacion, codigo_postal, pais)
        return ("Address updated", 200)
    except Exception as e:
        print('api_address_update error:', e)
        return (f"Error updating address: {e}", 500)
    
@app.route('/api/pedidos', methods=['GET'])
@login_required
def api_pedidos():
    client_id = request.args.get('client_id')
    date_from = request.args.get('date_from')
    date_to = request.args.get('date_to')
    pedidos = db.list_pedidos(client_id, date_from, date_to)
    return jsonify(pedidos)


@app.route('/api/pedidos/<int:pedido_id>/lines', methods=['GET'])
@login_required
def api_pedido_lines(pedido_id):
    """Return the lines for a given pedido id.
    Uses database.get_pedido_lines to fetch enriched product info when available.
    """
    try:
        lines = db.get_pedido_lines(pedido_id)
        return jsonify(lines)
    except Exception as e:
        print('api_pedido_lines error:', e)
        return jsonify([]), 500


@app.route('/api/pedidos/assign', methods=['POST'])
@login_required
def api_pedidos_assign():
    """Accept assignment payloads per line/process and write to assignaciones table.

    Expected JSON body: { "pedido": <id>, "idlinia": <idlinia>, "proceso": "cortado", "empleado": <id>, "maquina": <id?> }
    """
    payload = request.get_json(silent=True)
    if not payload:
        return ("Missing JSON payload", 400)

    pedido = payload.get('pedido') or payload.get('pedido_id') or payload.get('id')
    idlinia = payload.get('idlinia') or payload.get('linea') or payload.get('id')
    proceso = payload.get('proceso')
    empleado = payload.get('empleado') or payload.get('employee_id') or payload.get('empleado_id')
    maquina = payload.get('maquina') if 'maquina' in payload else None

    if not pedido or not idlinia or not proceso:
        return ("Missing required fields (pedido, idlinia, proceso, empleado)", 400)

    try:
        if db.pedido_assigned(pedido, proceso, idlinia):
            db.update_assignment(pedido, empleado, proceso, idlinia)
        else:
            db.add_assignment(pedido, empleado, proceso, idlinia)
        return ("Assignment saved", 201)
    except Exception as e:
        print('api_pedidos_assign error:', e)
        return (f"Error saving assignment: {e}", 500)
    
@app.route('/api/pedidos/assigned', methods=['POST'])
@login_required
def api_pedidos_assigned():
    # Accept JSON body or form data / query param for flexibility
    pedido = None
    if request.is_json:
        pedido = request.json.get('pedido') or request.json.get('id')
    else:
        pedido = request.form.get('pedido') or request.args.get('pedido')

    if not pedido:
        return jsonify([]), 400

    try:
        results = db.get_assignments_for_pedido(pedido)
        return jsonify(results)
    except Exception as e:
        print('api_pedidos_assigned error:', e)
        return jsonify([]), 500



@app.route('/api/assignaciones', methods=['GET'])
@login_required
def api_assignaciones():
    # Return assignments for the current session user by default
    employee = request.args.get('employee')
    try:
        if not employee:
            # use session username
            user = session.get('user')
            if not user:
                return ("Not authenticated", 401)
            results = db.get_assignments_for_user(user)
        else:
            # allow querying by username
            results = db.get_assignments_for_user(employee)
        return jsonify(results)
    except Exception as e:
        print('api_assignaciones error:', e)
        return jsonify([]), 500


@app.route('/api/assignaciones/update', methods=['POST'])
@login_required
def api_assignaciones_update():
    payload = request.get_json(silent=True)
    if not payload:
        return ("Missing JSON payload", 400)
    pedido = payload.get('pedido')
    idlinia = payload.get('idlinia')
    proceso = payload.get('proceso')
    empleado = payload.get('empleado')
    maquina = payload.get('maquina') if 'maquina' in payload else None
    estado = payload.get('estado') if 'estado' in payload else None
    
    # If empleado not provided, default to current session user id
    if not empleado:
        cur_user = session.get('user')
        if not cur_user:
            return ("Not authenticated", 401)
        users = db.get_users(cur_user)
        if not users:
            return ("Employee not found", 404)
        empleado = users[0].get('id')

    if not all([pedido, idlinia, proceso, empleado]):
        return ("Missing required fields (pedido, idlinia, proceso, empleado)", 400)

    try:
        db.update_assignment(pedido, empleado, proceso, idlinia, maquina, estado)
        db.check_pedido_status(pedido)
        return ("Assignment updated", 200)
    except Exception as e:
        print('api_assignaciones_update error:', e)
        return (f"Error updating assignment: {e}", 500)


@app.route('/api/maquinas', methods=['GET'])
@login_required
def api_maquinas():
    try:
        rows = db.list_machines()
        return jsonify(rows)
    except Exception as e:
        print('api_maquinas error:', e)
        return jsonify([]), 500
    
#API: processes list
@app.route('/api/processes', methods=['GET'])
@login_required
def api_processes():
    try:
        processes = db.list_processes()
        return jsonify(processes)
    except Exception as e:
        print('api_processes error:', e)
        return jsonify([])

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
    department = request.form.get('department', None)
    if not db.check_params([user, password]):
        abort(400)

    if db.check_username(user):
        return ("Username already exists", 409)

    hashed_password = encrypt_password(password)
    # store as utf-8 string in DB
    if isinstance(hashed_password, bytes):
        hashed_password = hashed_password.decode('utf-8')

    db.create_user(user, hashed_password, privilege, department)
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
    q = session.get('user', '')
    menu = db.load_menu(q)
    return jsonify(menu)

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


#clients edit page & update 
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

#PEDIDOS MANAGEMENT

#listar pedidos
@app.route('/pedidos', methods=['GET'])
@login_required
def pedidos_list():
    return render_template('pedidos/pedidos_list.html')

#Añadir pedidos
@app.route('/pedidos/add', methods=['GET', 'POST'])
@login_required
def pedidos():
    if request.method == 'GET':
        return render_template('pedidos/pedidos_add.html')
    # POST -> add pedido
    client = request.json.get('cliente')
    direccion = request.json.get('direccion_envio')
    email = request.json.get('contacto_email')
    checkbox = str(request.json.get('factura_pendiente'))
    print('Checkbox value:', checkbox)
    lines = request.json.get('lines')  # Expecting a list of dicts with 'producto' and 'cantidad'
    if not client or not direccion or not lines:
        return ("Missing parameters", 400)
    try:
        pedido = db.add_pedido(client, direccion)
        for i in lines:
            db.add_linea_pedido(pedido, i['producto'], i['cantidad'])
        future = executor.submit(files.generate_invoice, pedido)
        response = future.result()
        file_path = response
        db.upload_invoice(client=client, file_path=file_path, email=email, checkbox=checkbox, pedido=pedido)
        payload = {
            'to': session.get('user'),
            'mensaje': 'Se ha añadido un nuevo pedido asignalo!!'
        }
        ntf.send_notification(payload=payload, socketio=socketio)
        #socketio.emit('notificacion', {'usuario': client, 'mensaje': 'Se ha añadido un nuevo pedido asignalo'})
        return ("Pedido added", 201)
    except Exception as e:
        print('pedidos_add error:', e)
        return (f"Error adding pedido: {e}", 500)

#detalles del pedido
@app.route('/pedidos/detalles', methods=['GET'])
@login_required
def pedido_details():
    user_dept = db.get_departments(session.get('user'))
    pedido_id = request.args.get('id')
    if user_dept[0]['iddept'] != 6:
        return render_template('pedidos/pedido_details.html', pedido_id=pedido_id)
    elif user_dept[0]['iddept'] == 6:
        return render_template('pedidos/pedido_details_internal.html', pedido_id=pedido_id)

#Eliminar pedidos
@app.route('/pedidos/delete', methods=['GET', 'POST'])
@login_required
def pedidos_delete():
    if request.method == 'GET':
        return render_template('pedidos/pedidos_delete.html')
    # POST -> delete pedido
    pedido_id = request.form.get('id')
    if not pedido_id:
        return ("Missing id", 400)
    try:
        db.delete_pedido(pedido_id)
        payload = {
            'to': session.get('user'),
            'mensaje': 'Se ha eliminado un pedido!!'
        }
        ntf.send_notification(payload=payload, socketio=socketio)
        return ("Pedido deleted", 200)
    except Exception as e:
        print('pedidos_delete error:', e)
        return (f"Error deleting pedido: {e}", 500)


@app.route('/pedidos/assign', methods=['GET'])
@login_required
def pedidos_assign_page():
    # Render the assign UI; the page's JS reads ?id=<pedido> from the query string.
    pedido_id = request.args.get('id')
    return render_template('pedidos/pedidos_assign.html', pedido_id=pedido_id)


@app.route('/pedidos/assigned', methods=['GET'])
@login_required
def pedidos_assigned_page():
    # Render the assigned UI; the page's JS reads ?id=<pedido> from the query string.
    return render_template('pedidos/my_assignments.html')

@app.route('/pedidos/assignment_detail', methods=['GET'])
@login_required
def pedidos_assignment_detail_page():
    pedido_id = request.args.get('pedido')
    line_id = request.args.get('idlinea')
    proces = request.args.get('proceso')
    return render_template('pedidos/assignment_detail.html', pedido_id=pedido_id, line_id=line_id, proceso=proces)


@app.route('/products', methods=['GET'])
@login_required
def products_list():
    return render_template('productos/products_list.html')

@app.route("/products/detail", methods=['GET'])
@login_required
def product_details():
    product_id = request.args.get('id')
    return render_template('productos/product_detail.html', product_id=product_id)


@app.route('/products/add', methods=['GET', 'POST'])
@login_required
def products_add():
    if request.method == 'GET':
        return render_template('productos/product_add.html')

    # POST -> create product
    nombre = request.form.get('nombre')
    codigo = request.form.get('codigo')
    descripcion = request.form.get('descripcion')
    precio = request.form.get('precio')

    # handle planos upload
    planos_file = request.files.get('planos')
    planos_filename = None
    if planos_file and planos_file.filename:
        filename = secure_filename(planos_file.filename)
        planos_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'files', 'planos'))
        os.makedirs(planos_dir, exist_ok=True)
        save_path = os.path.join(planos_dir, filename)
        planos_file.save(save_path)
        planos_filename = filename

    # create product in DB
    try:
        pid = db.create_product(nombre, codigo, descripcion, precio if precio!='' else None, planos_filename)
    except Exception as e:
        print('create_product error', e)
        abort(500)

    # despiece entries: form provides arrays for name, codigo and optional plano file
    pieza_names = request.form.getlist('despiece_name[]')
    pieza_codigos = request.form.getlist('despiece_codigo[]')
    pieza_files = request.files.getlist('despiece_plano[]')
    try:
        for i, pname in enumerate(pieza_names):
            if not pname or not pname.strip():
                continue
            pcodigo = pieza_codigos[i] if i < len(pieza_codigos) else None
            plano_filename_piece = None
            if i < len(pieza_files):
                pf = pieza_files[i]
                if pf and pf.filename:
                    safe = secure_filename(pf.filename)
                    planos_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'files', 'planos'))
                    os.makedirs(planos_dir, exist_ok=True)
                    save_name = f"pieza_prod{pid}_{i}_{safe}"
                    pf.save(os.path.join(planos_dir, save_name))
                    plano_filename_piece = save_name

            # create pieza and relation
            try:
                pieza_id = db.create_pieza(pname, pcodigo, plano_filename_piece)
                db.add_despiece(pid, pieza_id)
            except Exception as e:
                print('error inserting pieza/despiece', e)
                # continue with next pieza
    except Exception as e:
        print('add_despiece error', e)

    return redirect(url_for('product_details') + '?id=' + str(pid))


@app.route('/api/piezas', methods=['GET'])
@login_required
def api_piezas():
    try:
        name = request.args.get('name')
        code = request.args.get('code')
        rows = db.list_piezas(name=name, code=code)
        return jsonify(rows)
    except Exception as e:
        print('api_piezas error', e)
        return jsonify([])


@app.route('/api/producto/piezas', methods=['GET'])
@login_required
def api_producto_piezas():
    pid = request.args.get('id')
    if not pid:
        return jsonify([])
    try:
        rows = db.get_piezas_by_producto(pid)
        return jsonify(rows)
    except Exception as e:
        print('api_producto_piezas error', e)
        return jsonify([])


@app.route('/products/despiece', methods=['GET'])
@login_required
def products_despiece():
    user_dept = db.get_departments(session.get('user'))
    if user_dept[0]['iddept'] != 6:
        return render_template('productos/product_despiece.html')
    elif user_dept[0]['iddept'] == 6:
        return render_template('productos/product_despiece _internal.html')


@app.route('/piezas/list', methods=['GET'])
@login_required
def piezas_lsit():
    return render_template('productos/piezas/piezas_list.html')

@app.route('/facturas/generate', methods=['POST'])
@internal_required
def facturas_generate():
    print('Received invoice generation request:', request.json)
    pedido_id = request.json.get('pedido_id')   
    path = files.generate_invoice(pedido_id)
    return path, 201

@app.route('/test')
def test_page():
    return render_template('test.html')


@app.route('/test/notify', methods=['POST'])
def test_notify():
    """Test endpoint: accept JSON { to: username|'all'|'broadcast', message: str, persist: bool }
    This endpoint is unauthenticated (kept for testing) and will store the notification and emit it.
    """
    try:
        data = None
        try:
            data = request.get_json(silent=True)
        except Exception:
            data = None
        to = None
        message = 'Mensaje de prueba desde /test/notify'
        persist = True
        if isinstance(data, dict):
            to = data.get('to')
            message = data.get('message', message)
            persist = data.get('persist', True)

        # store notification
        try:
            # remitente is 'test' for this endpoint
            nid = None
            try:
                nid = db.add_notification(to if to and to != 'all' else None, 'test', message, metadata=None, persist=persist)
            except Exception as e:
                print('Could not persist notification:', e)

            # emit
            if not to or to == 'all' or to == 'broadcast':
                socketio.emit('notificacion', {'usuario': 'test', 'mensaje': message})
            elif isinstance(to, list):
                for u in to:
                    socketio.emit('notificacion', {'usuario': 'test', 'mensaje': message}, room=str(u))
            else:
                socketio.emit('notificacion', {'usuario': 'test', 'mensaje': message}, room=str(to))
        except Exception as e:
            print('Error emitting/storing test notification:', e)
        return ('Notificación enviada', 200)
    except Exception as e:
        print('test_notify error:', e)
        return (f'Error: {e}', 500)


@app.route('/api/notify', methods=['POST'])
@login_required
def api_notify():
    """Send a notification from the logged-in user to one or many recipients.
    JSON body: { to: <username>|[usernames]|'all', message: <str>, persist: <bool, default true> }
    """
    print("called")
    payload = request.get_json(silent=True)
    if not payload or 'message' not in payload:
        return ("Missing message", 400)
    sender = session.get('user') or 'system'
    to = payload.get('to')
    message = payload.get('message')
    persist = payload.get('persist', True)
    url = payload.get('url', None)
    try:
        # persist and emit
        if not to or to == 'all' or to == 'broadcast':
            db.add_notification(None, sender, message, metadata=None, persist=persist)
            socketio.emit('notificacion', {'usuario': sender, 'mensaje': message, 'url': url})
        elif isinstance(to, list):
            for u in to:
                db.add_notification(u, sender, message, metadata=None, persist=persist)
                socketio.emit('notificacion', {'usuario': sender, 'mensaje': message, 'url': url}, room=str(u))
        else:
            db.add_notification(to, sender, message, metadata=None, persist=persist)
            socketio.emit('notificacion', {'usuario': sender, 'mensaje': message, 'url': url}, room=str(to))
        return ('Notification sent', 201)
    except Exception as e:
        print('api_notify error:', e)
        return (f'Error: {e}', 500)


@app.route('/api/notifications', methods=['GET'])
@login_required
def api_list_notifications():
    user = session.get('user')
    only_unread = request.args.get('unread') == '1'
    try:
        rows = db.get_notifications_for_user(user, only_unread=only_unread)
        return jsonify(rows)
    except Exception as e:
        print('api_list_notifications error:', e)
        return jsonify([])


@app.route('/api/notifications/mark_read', methods=['POST'])
@login_required
def api_mark_read():
    payload = request.get_json(silent=True)
    if not payload or 'id' not in payload:
        return ("Missing id", 400)
    nid = payload.get('id')
    user = session.get('user')
    try:
        ok = db.mark_notification_as_read(nid, user)
        if ok:
            return ('Marked', 200)
        return ('Not found or forbidden', 404)
    except Exception as e:
        print('api_mark_read error:', e)
        return (f'Error: {e}', 500)

if __name__ == '__main__':
    socketio.run(app, debug=True, host='0.0.0.0', port=80, log_output=False)
