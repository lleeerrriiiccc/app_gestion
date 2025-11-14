from flask import jsonify
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

def read_data(query, params=None):
    conn = connect()
    cursor = conn.cursor(dictionary=True)
    if params:
        cursor.execute(query, params)
    else:
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

def get_users(username=None, dept=None):
    if username is None and dept is None:
        query = "SELECT * FROM users"
        conn = connect()
        cursor = conn.cursor(dictionary=True)
        cursor.execute(query)
        results = cursor.fetchall()
        cursor.close()
        conn.close()
        return results
    elif dept is not None:
        query = "SELECT user, id FROM users WHERE dept = %s"
        response = read_data(query, (dept,))
        return response
    elif username is not None:
        conn = connect()
        cursor = conn.cursor(dictionary=True)
        query = "SELECT * FROM users WHERE user = %s"
        cursor.execute(query, (username,))
        results = cursor.fetchall()
        cursor.close()
        conn.close()
        return results
    elif username is not None and dept is not None:
        query = "SELECT * FROM users WHERE user = %s AND dept = %s"
        response = read_data(query, (username, dept))
        return response
    return "Error: No parameters provided."

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


def delete_contact(contact_id):
    """Delete a contact from datos_contacto by its idcontacto."""
    conn = connect()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM datos_contacto WHERE idcontacto = %s", (contact_id,))
    conn.commit()
    cursor.close()
    conn.close()


def delete_address(idregistro):
    """Delete a shipping address from datos_envio by its idregistro."""
    conn = connect()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM datos_envio WHERE idregistro = %s", (idregistro,))
    conn.commit()
    cursor.close()
    conn.close()

def update_contact(contact_id, client_id, name, email, tel, facturas):
    params = (client_id, name, email, tel, facturas, contact_id)
    for p in params:
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

def update_address(address_id, client_id, direccion, poblacion, codigo_postal, pais):
    params = (client_id, direccion, poblacion, codigo_postal, pais, address_id)
    for p in params:
        if check_params([p]) is False:
            raise ValueError("Invalid parameter detected.")
        elif check_params([p]) is True:
            continue
    """Update an existing contact's information in datos_contacto."""
    conn = connect()
    cursor = conn.cursor()
    cursor.execute(
        "UPDATE datos_envio SET direccion = %s, poblacion = %s, codigo_postal = %s, pais = %s WHERE idregistro = %s AND cliente = %s",
        (direccion, poblacion, codigo_postal, pais, address_id, client_id)
    )
    conn.commit()
    cursor.close()
    conn.close()


def load_menu(user):
    if check_params([user]) is False:
        raise ValueError("Invalid department parameter.")
    dept_query = "SELECT dept FROM users WHERE user = %s"
    menu_query = "SELECT menu FROM departamentos WHERE iddept = %s"
    dept = read_data(dept_query, (user,))
    if not dept:
        return None
    dept_id = dept[0]['dept']
    menu_data = read_data(menu_query, (dept_id,))
    if not menu_data:
        return None
    menu = menu_data[0]['menu']
    menu = str(menu)
    menu = json.loads(menu)
    return menu


def add_pedido(cliente_id, direccion_envio):
    """Insert a new pedido and return its id."""
    conn = connect()
    cursor = conn.cursor()
    cursor.execute("INSERT INTO pedidos (cliente, direccion_envio) VALUES (%s, %s)", (cliente_id, direccion_envio))
    conn.commit()
    pedido_id = cursor.lastrowid
    cursor.close()
    conn.close()
    return pedido_id


def add_linea_pedido(pedido_id, producto_id, cantidad):
    """Insert a new line into linias_pedido."""
    conn = connect()
    cursor = conn.cursor()
    cursor.execute("INSERT INTO linias_pedido (pedido, producto, cantidad) VALUES (%s, %s, %s)", (pedido_id, producto_id, cantidad))
    conn.commit()
    cursor.close()
    conn.close()


def products_list(q='*'):
    """Return list of products. If q provided, performs a LIKE search on `nombre`."""
    conn = connect()
    cursor = conn.cursor(dictionary=True)
    try:
        if q and q != '*':
            term = q + '%'
            cursor.execute("SELECT idproducto, nombre, descripcion, codigo, precio FROM producto WHERE nombre LIKE %s LIMIT 200", (term,))
        else:
            cursor.execute("SELECT idproducto, nombre, descripcion, codigo, precio FROM producto LIMIT 200")
        rows = cursor.fetchall()
    finally:
        cursor.close()
        conn.close()
    return rows

def list_pedidos(cliente_id):
    if cliente_id:
        """Return list of pedidos with client names."""
        query = """
        SELECT 
        pedidos.idpedido, 
        clientes.name AS cliente, 
        pedidos.direccion_envio, 
        DATE_FORMAT(pedidos.fecha_taller, '%d-%m-%Y'),
        pedidos.estado,
        pedidos.cliente AS cliente_id
        FROM pedidos
        INNER JOIN clientes ON pedidos.cliente = clientes.idcliente
        WHERE pedidos.cliente = %s
        LIMIT 500;
        """
        results = read_data(query, (cliente_id,))
    else:
        query = """
        SELECT 
        pedidos.idpedido, 
        clientes.name AS cliente, 
        pedidos.direccion_envio, 
        DATE_FORMAT(pedidos.fecha_taller, '%d-%m-%Y') AS fecha_taller,
        pedidos.estado,
        pedidos.cliente AS cliente_id
        FROM pedidos
        INNER JOIN clientes ON pedidos.cliente = clientes.idcliente
        LIMIT 500;
        """
        results = read_data(query)
    return results


def get_pedido_lines(pedido_id):
    """Return full pedido info and its line items, including product info."""   

    lines_query = """
    SELECT lp.idlinia, lp.producto, pr.nombre AS producto_nombre, pr.codigo AS producto_codigo, pr.precio AS producto_precio, lp.cantidad
    FROM linias_pedido lp
    LEFT JOIN producto pr ON lp.producto = pr.idproducto
    WHERE lp.pedido = %s
    """
    results_lines = read_data(lines_query, (pedido_id,))

    return results_lines


def update_pedido_address(pedido_id, direccion_id):
    conn = connect()
    cursor = conn.cursor()
    cursor.execute("UPDATE pedidos SET direccion_envio = %s WHERE idpedido = %s", (direccion_id, pedido_id))
    conn.commit()
    cursor.close()
    conn.close()

def get_pedido(pedido_id):
    """Return full pedido info for a given pedido_id."""   
    pedido_query = """
    SELECT 
    pedidos.idpedido, 
    pedidos.cliente AS cliente_id,
    clientes.name AS cliente_nombre,
    pedidos.direccion_envio, 
    DATE_FORMAT(pedidos.fecha_taller, '%d-%m-%Y') AS fecha_taller,
    pedidos.estado
    FROM pedidos
    INNER JOIN clientes ON pedidos.cliente = clientes.idcliente
    WHERE pedidos.idpedido = %s
    """
    results_pedido = read_data(pedido_query, (pedido_id,))

    if results_pedido:
        return results_pedido[0]
    else:
        return None

def get_direccion_envio(address_id):
    """Return full address info for a given address_id from datos_envio."""   
    address_query = """
    SELECT 
    idregistro,
    cliente,
    direccion,
    poblacion,
    codigo_postal,
    pais
    FROM datos_envio
    WHERE idregistro = %s
    """
    results_address = read_data(address_query, (address_id,))

    if results_address:
        return results_address[0]
    else:
        return None


def add_assignment(pedido, empleado, proceso, idlinia, maquina=None):
    """Insert an assignment into the assignaciones table.

    Expects: pedido (int), empleado (int), proceso (str or int), idlinia (int), maquina (int or None)
    """
    conn = connect()
    cursor = conn.cursor()
    try:
        cursor.execute(
            "INSERT INTO assignaciones (pedido, empleado, proceso, idlinia, maquina) VALUES (%s, %s, %s, %s, %s)",
            (pedido, empleado, proceso, idlinia, maquina)
        )
        conn.commit()
    finally:
        cursor.close()
        conn.close()

def list_processes():
    """Return list of distinct processes from assignaciones table."""
    query = "SELECT DISTINCT idproceso AS id, descripcion AS nombre FROM procesos;"
    results = read_data(query)
    return results



