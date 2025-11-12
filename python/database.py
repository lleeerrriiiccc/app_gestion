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
    cur.execute("INSERT INTO facturas (cliente, ubicacion_factura, factura_pendiente, email) VALUES ((SELECT idcliente FROM clientes WHERE NAME = %s), %s, %s, %s)", (client, file_path, factura_pendiente, email))
    conn.commit()
    cur.close()
    conn.close()

def check_clients(client):
    conn = connect()
    cursor = conn.cursor()
    client = client + '%'
    cursor.execute("SELECT name FROM clientes WHERE NAME LIKE %s;", (client,))
    rows = cursor.fetchall()
    print(rows)
    cursor.close()
    conn.close()
    if rows:
        return rows
    else:
        return False
    
def delete_invoice(invoice_id):
    conn = connect()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM facturas WHERE idfactura = %s", (invoice_id,))
    conn.commit()
    cursor.close()
    conn.close()

def clients_info(client="*"):
    if client != "*":
        client = client + '%'
        query = "select * from clientes where name like %s;"    
        conn = connect()
        cursor = conn.cursor(dictionary=True)
        cursor.execute(query, (client,))
        results = cursor.fetchall()
        cursor.close()
        conn.close()
        return results
    query = "select * from clientes;"    
    conn = connect()
    cursor = conn.cursor(dictionary=True)
    cursor.execute(query)
    results = cursor.fetchall()
    cursor.close()
    conn.close()
    return results


def update_client(client_id, name, nif):
    """Update client's basic info in clientes table."""
    conn = connect()
    cursor = conn.cursor()
    cursor.execute("UPDATE clientes SET name = %s, nif = %s WHERE idcliente = %s", (name, nif, client_id))
    conn.commit()
    cursor.close()
    conn.close()

def contact_info(id):
    query = "select * from datos_contacto where cliente = %s;"    
    conn = connect()
    cursor = conn.cursor(dictionary=True)
    cursor.execute(query, (id,))
    results = cursor.fetchall()
    cursor.close()
    conn.close()
    return results

def addresses_info(client_id):
    """Return shipping/address records for a given client id from datos_envio."""
    query = "select * from datos_envio where cliente = %s;"
    conn = connect()
    cursor = conn.cursor(dictionary=True)
    cursor.execute(query, (client_id,))
    results = cursor.fetchall()
    cursor.close()
    conn.close()
    return results


def add_contact(client_id, name, email, tel, facturas):
    """Insert a new contact into datos_contacto for a client.
    Assumes idcontacto is AUTO_INCREMENT or optional in the schema.
    """
    conn = connect()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO datos_contacto (cliente, name, email, tel, facturas) VALUES (%s, %s, %s, %s, %s)",
        (client_id, name, email, tel, facturas)
    )
    conn.commit()
    cursor.close()
    conn.close()


def add_address(client_id, direccion, poblacion, codigo_postal, pais):
    """Insert a new shipping address into datos_envio for a client."""
    conn = connect()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO datos_envio (cliente, poblacion, codigo_postal, direccion, pais) VALUES (%s, %s, %s, %s, %s)",
        (client_id, poblacion, codigo_postal, direccion, pais)
    )
    conn.commit()
    cursor.close()
    conn.close()

def add_client(name, nif):
    """Insert a new client into clientes table.
    Updated to accept name and email (email may be stored in 'email' column).
    """
    conn = connect()
    cursor = conn.cursor()
    try:
        cursor.execute("INSERT INTO clientes (name, email) VALUES (%s, %s)", (name, nif))
    except Exception:
        # fallback if table uses 'nif' column
        cursor.execute("INSERT INTO clientes (name, nif) VALUES (%s, %s)", (name, nif))
    conn.commit()
    cursor.close()
    conn.close()

def update_contact(contact_id, client_id, name, email, tel, facturas):
    params = (client_id, name, email, tel, facturas, contact_id)
    for p in params:
        print(p)
        if check_params([p]) is False:
            raise ValueError("Invalid parameter detected.")
        elif check_params([p]) is True:
            continue
    """Update an existing contact's information in datos_contacto."""
    conn = connect()
    cursor = conn.cursor()
    cursor.execute(
        "UPDATE datos_contacto SET name = %s, email = %s, tel = %s, facturas = %s WHERE idcontacto = %s AND cliente = %s",
        (name, email, tel, facturas, contact_id, client_id)
    )
    conn.commit()
    cursor.close()
    conn.close()
