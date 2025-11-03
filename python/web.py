import os
from flask import Flask, render_template, request, redirect, url_for, session, abort, jsonify
from database import *
from encription import *
from werkzeug.utils import secure_filename
import os
from flask import send_from_directory

# Use the repository's web/html folder as the template folder
template_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'web', 'html'))
app = Flask(__name__, template_folder=template_dir)

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




@app.route('/dashboard')
@login_required
def dashboard():
    return render_template('dashboard.html')


@app.route('/users', methods=['GET'])
def users():
    # Allow public POST so users can self-register.
    # For GET, require login to view the register module inside the dashboard;
    # if not logged in, redirect to login page.
    if request.method == 'GET':
        if 'user' not in session:
            return redirect(url_for('login'))
        return render_template('register.html')




# Upload endpoint for invoices
@app.route('/invoice', methods=["GET"])
@login_required
def invoice():
    if request.method == 'GET':
        if 'user' not in session:
            return redirect(url_for('login'))
        return render_template('upload_fragment.html')
    # ensure upload folder exists under repo/files/bills
    
    
@app.route('/menu', methods=['GET'])
def menu():
    import json
    with open(os.path.join(template_dir, 'menu.json'), 'r') as f:
        menu_data = json.load(f)
    return jsonify(menu_data)


if __name__ == '__main__':
    app.run(debug=True, port=80)
