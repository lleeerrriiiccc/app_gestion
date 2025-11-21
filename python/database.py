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

def write_data(query, params=None):
    conn = connect()
    cursor = conn.cursor()
    if params:
        cursor.execute(query, params)
    else:
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

def upload_invoice(client, file_path, email, checkbox, pedido):
    conn = connect()
    cur = conn.cursor()
    # factura_pendiente: interpret checkbox as 0 when 'on', else 1 to keep parity with original app
    cur.execute("INSERT INTO facturas (cliente, ubicacion_factura, factura_pendiente, email, pedido, fecha) VALUES (%s, %s, %s, %s, %s, (DATE(NOW())))", (client, file_path, checkbox, email, pedido))
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

def delete_pedido(pedido_id):
    """Delete a pedido by its id."""
    conn = connect()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM pedidos WHERE idpedido = %s", (pedido_id,))
    conn.commit()
    cursor.close()
    conn.close()


def add_linea_pedido(pedido_id, producto_id, cantidad):
    """Insert a new line into linias_pedido."""
    conn = connect()
    cursor = conn.cursor()
    cursor.execute("INSERT INTO linias_pedido (pedido, producto, cantidad) VALUES (%s, %s, %s)", (pedido_id, producto_id, cantidad))
    conn.commit()
    cursor.close()
    conn.close()


def products_list(q='*', idproducto=None):
    """Return list of products. If q provided, performs a LIKE search on `nombre`."""
    conn = connect()
    cursor = conn.cursor(dictionary=True)
    try:
        if q and q != '*':
            term = '%' + q + '%'
            cursor.execute("SELECT idproducto, nombre, descripcion, codigo, precio, planos FROM producto WHERE nombre LIKE %s OR codigo LIKE %s LIMIT 200", (term, term))
        elif idproducto is not None:
            cursor.execute("SELECT idproducto, nombre, descripcion, codigo, precio, planos FROM producto WHERE idproducto = %s LIMIT 200", (idproducto,))
        else:
            cursor.execute("SELECT idproducto, nombre, descripcion, codigo, precio, planos FROM producto LIMIT 200")
        rows = cursor.fetchall()
    finally:
        cursor.close()
        conn.close()
    return rows

def create_product(nombre, codigo=None, descripcion=None, precio=None, planos=None):
    """Insert a product into `producto` and return the new id."""
    conn = connect()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO producto (nombre, codigo, descripcion, precio, planos) VALUES (%s, %s, %s, %s, %s)",
        (nombre, codigo, descripcion, precio, planos)
    )
    conn.commit()
    pid = cursor.lastrowid
    cursor.close()
    conn.close()
    return pid

def add_despiece(producto_id, pieza_id):
    """Insert a despiece row into `despiece_productos`."""
    conn = connect()
    cursor = conn.cursor()
    cursor.execute("INSERT INTO despiece_productos (producto, pieza) VALUES (%s, %s)", (producto_id, pieza_id))
    conn.commit()
    cursor.close()
    conn.close()

def list_piezas(name=None, code=None):
    if name is None and code is None:
        """Return list of piezas (idpiezas, name, codigo)."""
        query = "SELECT idpiezas, name, codigo FROM piezas"
    if name is None and code is not None:
        """Return list of piezas filtered by code."""
        query = """
        SELECT 
            p.idpiezas,
            p.name AS nombre_pieza,
            p.codigo AS codigo_pieza,
            pr.idproducto,
            pr.nombre AS nombre_producto,
            pr.codigo AS codigo_producto
        FROM piezas p
        INNER JOIN despiece_productos dp ON p.idpiezas = dp.pieza
        INNER JOIN producto pr ON dp.producto = pr.idproducto
        WHERE p.codigo LIKE %s
        """
        return read_data(query, (f'%{code}%',))
    if name is not None and code is None:
        """Return list of piezas filtered by name."""
        query = """
        SELECT 
            p.idpiezas,
            p.name AS nombre_pieza,
            p.codigo AS codigo_pieza,
            pr.idproducto,
            pr.nombre AS nombre_producto,
            pr.codigo AS codigo_producto
        FROM piezas p
        INNER JOIN despiece_productos dp ON p.idpiezas = dp.pieza
        INNER JOIN producto pr ON dp.producto = pr.idproducto
        WHERE p.name LIKE %s
        """
        return read_data(query, (f'%{name}%',))


def get_piezas_by_producto(producto_id):
    """Return piezas linked to a producto via despiece_productos.

    Returns list of dicts: idpiezas, name, codigo, plano
    """
    query = """
    SELECT p.idpiezas, p.name, p.codigo, p.plano
    FROM despiece_productos dp
    INNER JOIN piezas p ON dp.pieza = p.idpiezas
    WHERE dp.producto = %s
    """
    return read_data(query, (producto_id,))


def create_pieza(name, codigo=None, plano=None):
    """Insert a pieza into `piezas` and return the new idpiezas."""
    conn = connect()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO piezas (name, codigo, plano) VALUES (%s, %s, %s)",
        (name, codigo, plano)
    )
    conn.commit()
    pid = cursor.lastrowid
    cursor.close()
    conn.close()
    return pid

def list_pedidos(cliente_id=None, date_from=None, date_to=None):
    if cliente_id is not None:
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
    elif date_from is not None and date_to is not None:
        """Return list of pedidos within a date range."""
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
        WHERE pedidos.fecha_taller BETWEEN %s AND %s
        LIMIT 500;
        """
        results = read_data(query, (date_from, date_to))
    elif date_from is not None and date_to is None:
        """Return list of pedidos from a specific date onwards."""
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
        WHERE pedidos.fecha_taller >= %s
        LIMIT 500;
        """
        results = read_data(query, (date_from,))
    elif date_from is None and date_to is not None:
        """Return list of pedidos up to a specific date."""
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
        WHERE pedidos.fecha_taller <= %s
        LIMIT 500;
        """
        results = read_data(query, (date_to,))
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


def add_assignment(pedido, empleado, proceso, idlinia):
    """Insert an assignment into the assignaciones table.
    Expects: pedido (int), empleado (int), proceso (str or int), idlinia (int), maquina (int or None)
    """
    query = "INSERT INTO assignaciones (pedido, empleado, proceso, idlinia) VALUES (%s, %s, %s, %s)"
    write_data(query, (pedido, empleado, proceso, idlinia))
    query = "UPDATE pedidos SET assignado = 1 WHERE idpedido = %s"
    write_data(query, (pedido,))


def get_assignments_for_user(username):
    """Return assignments for a given username (employee username).

    Joins assignaciones -> pedidos -> clientes -> linias_pedido -> producto to provide useful fields.
    """
    query = """
    SELECT
    a.pedido,
    a.empleado,
    u.user AS empleado_user,
    proc.descripcion AS proceso,
    a.proceso AS idproceso,
    m.nombre AS maquina,
    a.idlinia,
    a.estado,
    DATE_FORMAT(p.fecha_taller, '%d-%m-%Y') AS fecha_taller,
    c.name AS cliente_name,
    lp.cantidad,
    pr.nombre AS producto_nombre
    FROM assignaciones a
        INNER JOIN users u ON a.empleado = u.id
        INNER JOIN pedidos p ON a.pedido = p.idpedido
        INNER JOIN procesos proc ON a.proceso = proc.idproceso
        LEFT JOIN maquinas m ON a.maquina = m.idmaquina
        LEFT JOIN clientes c ON p.cliente = c.idcliente
        LEFT JOIN linias_pedido lp ON a.idlinia = lp.idlinia
        LEFT JOIN producto pr ON lp.producto = pr.idproducto
    WHERE u.user = %s
        AND a.estado != 2  
        AND NOT EXISTS (
            SELECT 1 
            FROM assignaciones ant 
            WHERE ant.pedido = a.pedido 
                AND ant.idlinia = a.idlinia 
                AND ant.proceso = proc.idproceso - 1  
                AND ant.estado != 2  
        )
    ORDER BY p.fecha_taller DESC;
    """
    results = read_data(query, (username,))
    return results


def update_assignment(pedido, empleado, proceso, idlinia, maquina=None, estado=None):
    """Update assignment record setting maquina and/or estado. Matches row by pedido, empleado, proceso and idlinia."""
    # Build query dynamically to avoid overwriting with NULLs when values omitted
    data = {"pedido": pedido, "empleado": empleado, "proceso": proceso, "idlinia": idlinia}
    if maquina is None:
        maquina = 'null'
    if estado is None:
        estado = 'null'
    if empleado is None:
        empleado = 'null'
    data = {"pedido": pedido, "empleado": empleado, "proceso": proceso, "idlinia": idlinia, "maquina": maquina, "estado": estado}
    query = f"UPDATE assignaciones SET empleado = {data['empleado']}, maquina = {data['maquina']}, estado = {data['estado']} WHERE pedido = {data['pedido']} AND proceso = {data['proceso']} AND idlinia = {data['idlinia']};"
    conn = connect()
    cursor = conn.cursor()
    try:
        cursor.execute(query)
        
        conn.commit()
    finally:
        cursor.close()
        conn.close()


def list_machines():
    """Return list of machines from `maquinas` table."""
    query = "SELECT idmaquina, nombre, proceso FROM maquinas"
    return read_data(query)

def list_processes():
    """Return list of distinct processes from assignaciones table."""
    query = "SELECT DISTINCT idproceso AS id, descripcion AS nombre FROM procesos;"
    results = read_data(query)
    return results

def get_assignments_for_pedido(pedido_id):
    """Return assignments for a given pedido_id."""
    query = """
    SELECT
        a.pedido,
        a.empleado,
        u.user AS empleado_user,
        proc.descripcion AS proceso,
        a.proceso AS idproceso,
        m.nombre AS maquina,
        a.idlinia,
        a.estado
    FROM assignaciones a
        INNER JOIN procesos proc ON a.proceso = proc.idproceso
        LEFT JOIN users u ON a.empleado = u.id
        LEFT JOIN maquinas m ON a.maquina = m.idmaquina
    WHERE a.pedido = %s
    ORDER BY a.idlinia ASC;
    """
    results = read_data(query, (pedido_id,))
    return results

def pedido_assigned(pedido_id, proceso, idlinia):
    """Check if a pedido has any assignments."""
    query = "SELECT * FROM assignaciones WHERE pedido = %s AND proceso = %s AND idlinia = %s;"
    results = read_data(query, (pedido_id, proceso, idlinia))
    print(results)
    if results:
        return True
    else:
        return False
    
def last_invoice_number():
    """Return the last used invoice number from facturas table."""
    query = "SELECT MAX(idfactura) AS last_invoice FROM facturas;"
    results = read_data(query)
    if results and results[0]['last_invoice'] is not None:
        return results[0]['last_invoice']
    else:
        return 0



