import flask as fk
from flask import abort
import json
from database import *

app = fk.Flask(__name__)
@app.route('/')
def index():
    abort(403)

@app.route('/login')
def login():
    user = fk.request.args.get('username')
    password = fk.request.args.get('password')
    test = read_data(f"SELECT * FROM users WHERE user='{user}' AND pass='{password}'")
    if test:
        return "Welcome, " + user
    else:
        abort(401)


if __name__ == '__main__':
    app.run(debug=True)
