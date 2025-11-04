import os
from flask import Flask, render_template, request, redirect, url_for, session, abort, jsonify
from database import *
from encription import *
from werkzeug.utils import secure_filename
import mysql.connector
import os
from flask import send_from_directory
from flask_cors import CORS

# Use the repository's web/html folder as the template folder
template_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'web', 'html'))
app = Flask(__name__, template_folder=template_dir)

CORS(app)

# Simple secret for sessions (change in production)
app.secret_key = os.environ.get('FLASK_SECRET', 'dev-secret-key-change-me')


@app.route('/')
def index():
    return redirect(url_for('login'))


@app.route('/login', methods=['GET', 'POST'])
def login():
    # GET -> render login page
    if request.method == 'GET':
        return render_template('login.html')

    # POST -> authenticate
    user = request.form.get('username') or request.args.get('username')
    password = request.form.get('password') or request.args.get('password')

    if not check_params([user, password]):
        abort(400)

    res = get_users(user)
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


@app.route('/logout')
def logout():
    session.pop('user', None)
    return redirect(url_for('login'))


def login_required(f):
    from functools import wraps

    @wraps(f)
    def wrapped(*args, **kwargs):
        if 'user' not in session:
            return redirect(url_for('login'))
        return f(*args, **kwargs)

    return wrapped


# Serve css files from web/css at /css/<path:filename>
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
    if check_params([q]) is False:
        return jsonify([])
    clients = check_clients(q)
    if not clients:
        return jsonify([])
    return jsonify(clients)

# API: return users list for management UI
@app.route('/api/users', methods=['GET'])
@login_required
def api_users():
    try:
        results = get_users('*')
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


# Users edit (change password)
@app.route('/users/edit', methods=['GET', 'POST'])
@login_required
def users_edit():
    if request.method == 'GET':
        return render_template('users_edit.html')

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
        update_data("UPDATE users SET pass=%s WHERE user=%s", (hashed, username))
        return ("User updated", 200)
    except Exception as e:
        return (f"Error updating user: {e}", 500)


# Users delete
@app.route('/users/delete', methods=['GET', 'POST'])
@login_required
def users_delete():
    if request.method == 'GET':
        return render_template('users_delete.html')

    username = request.form.get('username')
    if not username:
        return ("Missing username", 400)
    try:
        delete_data("DELETE FROM users WHERE user = %s", (username,))
        return ("User deleted", 200)
    except Exception as e:
        return (f"Error deleting user: {e}", 500)

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


@app.route('/dashboard')
@login_required
def dashboard():
    return render_template('dashboard.html')


@app.route('/users/add', methods=['GET', 'POST'])
def users():
    # Allow public POST so users can self-register.
    # For GET, require login to view the register module inside the dashboard;
    # if not logged in, redirect to login page.
    if request.method == 'GET':
        if 'user' not in session:
            return redirect(url_for('login'))
        return render_template('user_add.html')

    # POST -> create user (public)
    user = request.form.get('username')
    password = request.form.get('password')
    privilege = request.form.get('privilege', 0)
    if not check_params([user, password]):
        abort(400)

    if check_username(user):
        return ("Username already exists", 409)

    hashed_password = encrypt_password(password)
    # store as utf-8 string in DB
    if isinstance(hashed_password, bytes):
        hashed_password = hashed_password.decode('utf-8')

    create_user(user, hashed_password, privilege)
    return ("User registered successfully", 201)


# Upload endpoint for invoices
@app.route('/invoices/add', methods=["GET", 'POST'])
@login_required
def invoice():
    if request.method == 'GET':
        if 'user' not in session:
            return redirect(url_for('login'))
        return render_template('upload_fragment.html')
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
            upload_invoice(client, file_path, email, checkbox)
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
    
@app.route('/menu', methods=['GET'])
def menu():
    import json
    with open(os.path.join(template_dir, 'menu.json'), 'r', encoding='utf-8') as f:
        menu_data = json.load(f)
    q = request.args.get('user', '')
    user = session.get('user', '')
    if privileges(user) == 1:
        return jsonify(menu_data["admin"])
    elif privileges(user) == 0:
        return jsonify(menu_data["user"])
    return abort(403)

@app.route('/api/me', methods=['GET'])
@login_required
def api_me():
    return jsonify({
        'user': session.get('user'),
        'privilege': session.get('privilege', 0)
    })

if __name__ == '__main__':
    app.run(debug=True, port=80)
