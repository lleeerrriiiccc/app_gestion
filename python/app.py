import flask as fk
from flask import abort
import json
from database import *
from encription import *

app = fk.Flask(__name__)
@app.route('/')
def index():
    abort(403)

@app.route('/login')
def login():
    user = fk.request.args.get('username')
    password = fk.request.args.get('password')
    test = read_data(f"SELECT * FROM users WHERE user='{user}'")
    if check_password(password.encode('utf-8'), test[0]['pass']) == True:
        return "Welcome, " + user
    else:
        abort(401)

@app.route('/register', methods=['POST'])
def register():
    user = str(fk.request.form.get('username'))
    password = str(fk.request.form.get('password'))
    hashed_password = encrypt_password(password)
    if check_username(user):
        return "Username already exists", 409
    else:
        write_data(f"INSERT INTO users (user, pass) VALUES ('{user}', '{hashed_password.decode('utf-8')}')")
        return "User registered successfully"


if __name__ == '__main__':
    app.run(debug=True)
