import mysql as db
import mysql.connector
import json

def connect():
    with open('data/conection.json', 'r') as file:
        config = json.load(file)
    
    connection = mysql.connector.connect(
        host=config['host'],
        user=config['username'],
        password=config['password'],
        database=config['database'],
        collation='utf8mb4_unicode_ci'
    )
    return connection

def read_data(query):
    conn = connect()
    cursor = conn.cursor(dictionary=True)
    cursor.execute(query)
    results = cursor.fetchall()
    cursor.close()
    conn.close()
    return results

def write_data(query):
    conn = connect()
    cursor = conn.cursor()
    cursor.execute(query)
    conn.commit()
    cursor.close()
    conn.close()

def update_data(query, data):
    conn = connect()
    cursor = conn.cursor()
    cursor.execute(query, data)
    conn.commit()
    cursor.close()
    conn.close()

def delete_data(query, data):
    conn = connect()
    cursor = conn.cursor()
    cursor.execute(query, data)
    conn.commit()
    cursor.close()
    conn.close()

def check_username(username):
    conn = connect()
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM users WHERE user = %s", (username,))
    count = cursor.fetchone()[0]
    cursor.close()
    conn.close()
    if count > 0:
        return True
    else:
        return False
    

def create_user(username, password, privilege=0):
    conn = connect()
    cursor = conn.cursor()
    cursor.execute("INSERT INTO users (user, pass, privilege) VALUES (%s, %s, %s)", (username, password, privilege))
    conn.commit()
    cursor.close()
    conn.close()

def get_users(username="*"):
    if username == "*":
        query = "SELECT * FROM users"
        conn = connect()
        cursor = conn.cursor(dictionary=True)
        cursor.execute(query)
        results = cursor.fetchall()
        cursor.close()
        conn.close()
        return results
    else:
        conn = connect()
        cursor = conn.cursor(dictionary=True)
        query = "SELECT * FROM users WHERE user = %s"
        cursor.execute(query, (username,))
        results = cursor.fetchall()
        cursor.close()
        conn.close()
    return results

def check_params(param:list):
    for p in param:
        payloads = "./data/exclusions.json"
        with open(payloads, 'r') as file:
            exclusions = json.load(file)
        if p in exclusions:
            return False
    return True

def privileges(username):
    conn = connect()
    cursor = conn.cursor()
    cursor.execute("SELECT privilege FROM users WHERE user = %s", (username,))
    result = cursor.fetchone()
    cursor.close()
    conn.close()
    if result:
        return result[0]
    else:
        return None
    
def check_privilege(requiered_privilege, user):
    user_privilege = privileges(user)
    if user_privilege is None:
        return False
    if user_privilege >= requiered_privilege:
        return True
    else:
        return False

def upload_invoice(client, file_path, email, checkbox):
    conn = connect()
    cur = conn.cursor()
    # factura_pendiente: interpret checkbox as 0 when 'on', else 1 to keep parity with original app
    factura_pendiente = 0 if checkbox == 'on' else 1
    cur.execute("INSERT INTO facturas (cliente, ubicacion_factura, factura_pendiente, email) VALUES (%s, %s, %s, %s)", (client, file_path, factura_pendiente, email))
    conn.commit()
    cur.close()
    conn.close()

def check_clients(client):
    conn = connect()
    cursor = conn.cursor()
    client = client + '%'
    cursor.execute("SELECT name FROM clientes WHERE NAME LIKE %s;", (client,))
    print("SELECT name FROM clientes WHERE NAME LIKE %s;", (client,))
    rows = cursor.fetchall()
    print(rows)
    cursor.close()
    conn.close()
    if rows:
        return rows
    else:
        return False

