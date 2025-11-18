# Documentación Técnica — Aplicación Flask `app_gestion`

## 1. Descripción General
La aplicación `app_gestion` es una solución basada en **Flask** que proporciona funcionalidades de gestión de usuarios, autenticación y operaciones sobre una base de datos relacional. El flujo principal se articula en torno a tres módulos clave:

- **`python/app.py`**: Punto de entrada de la aplicación Flask. Define los endpoints, gestiona las sesiones y coordina la lógica de negocio.
- **`python/database.py`**: Encapsula la conexión y operaciones con la base de datos. Proporciona funciones para consultas, inserciones y actualizaciones.
- **`python/encriptio.py`**: Implementa utilidades de cifrado y verificación de contraseñas, garantizando la seguridad de las credenciales de usuario.

---

## 2. Flujo de la Aplicación

1. **Inicio**  
   - Se inicializa la instancia de Flask y se configuran las rutas.  
   - Se establece la conexión con la base de datos a través de `database.py`.

2. **Autenticación**  
   - **Login (`/login`)**: Valida credenciales contra la tabla `users`.  
   - **Registro (`/register`)**: Inserta un nuevo usuario con contraseña cifrada.  

3. **Dashboard (`/dashboard`)**  
   - Ruta protegida por sesión.  
   - Muestra información agregada de la base de datos (usuarios, pedidos, facturas).  

4. **Operaciones de gestión**  
   - Endpoints para visualizar facturas, pedidos y despieces.  
   - Eliminación y actualización de registros.  

---

## 3. Detalle de Módulos y Funciones

### 3.1 `app.py`

*(Ya documentado previamente: login, register, dashboard, etc.)*

---

### 3.2 `database.py`

Este módulo implementa la capa de acceso a datos. Según `db_structure.md`, las tablas principales son:

- **`users`**: credenciales y datos de usuario.  
- **`orders`**: pedidos asociados a usuarios.  
- **`invoices`**: facturas generadas a partir de pedidos.  
- **`products`**: catálogo de productos y despieces.  

#### Funciones sobre `users`

- **`get_user(username)`**  
  - **Propósito:** Recuperar un usuario por nombre.  
  - **Entradas:** `username` (string).  
  - **Proceso:** `SELECT * FROM users WHERE username = ?`.  
  - **Salidas:** Diccionario con campos del usuario o `None`.  

- **`insert_user(username, password_hash, email)`**  
  - **Propósito:** Insertar un nuevo usuario.  
  - **Entradas:** `username`, `password_hash`, `email`.  
  - **Proceso:** `INSERT INTO users (...) VALUES (...)`.  
  - **Salidas:** `True` si éxito, `False` si error.  

- **`delete_user(user_id)`**  
  - **Propósito:** Eliminar un usuario por ID.  
  - **Entradas:** `user_id` (int).  
  - **Proceso:** `DELETE FROM users WHERE id = ?`.  
  - **Salidas:** `True` si éxito, `False` si no existe.  

---

#### Funciones sobre `orders`

- **`get_orders_by_user(user_id)`**  
  - **Propósito:** Listar pedidos de un usuario.  
  - **Entradas:** `user_id` (int).  
  - **Proceso:** `SELECT * FROM orders WHERE user_id = ?`.  
  - **Salidas:** Lista de pedidos.  

- **`insert_order(user_id, product_id, quantity)`**  
  - **Propósito:** Crear un nuevo pedido.  
  - **Entradas:** `user_id`, `product_id`, `quantity`.  
  - **Proceso:** `INSERT INTO orders (...) VALUES (...)`.  
  - **Salidas:** `True` si éxito, `False` si error.  

- **`delete_order(order_id)`**  
  - **Propósito:** Eliminar un pedido.  
  - **Entradas:** `order_id` (int).  
  - **Proceso:** `DELETE FROM orders WHERE id = ?`.  
  - **Salidas:** `True` si éxito, `False` si no existe.  

---

#### Funciones sobre `invoices`

- **`get_invoices()`**  
  - **Propósito:** Listar todas las facturas.  
  - **Entradas:** Ninguna.  
  - **Proceso:** `SELECT * FROM invoices`.  
  - **Salidas:** Lista de facturas.  

- **`get_invoice(invoice_id)`**  
  - **Propósito:** Recuperar una factura por ID.  
  - **Entradas:** `invoice_id` (int).  
  - **Proceso:** `SELECT * FROM invoices WHERE id = ?`.  
  - **Salidas:** Diccionario con datos de la factura o `None`.  

- **`insert_invoice(order_id, total_amount)`**  
  - **Propósito:** Crear una nueva factura.  
  - **Entradas:** `order_id`, `total_amount`.  
  - **Proceso:** `INSERT INTO invoices (...) VALUES (...)`.  
  - **Salidas:** `True` si éxito, `False` si error.  

---

#### Funciones sobre `products`

- **`get_products()`**  
  - **Propósito:** Listar todos los productos.  
  - **Entradas:** Ninguna.  
  - **Proceso:** `SELECT * FROM products`.  
  - **Salidas:** Lista de productos.  

- **`get_product(product_id)`**  
  - **Propósito:** Recuperar un producto por ID.  
  - **Entradas:** `product_id` (int).  
  - **Proceso:** `SELECT * FROM products WHERE id = ?`.  
  - **Salidas:** Diccionario con datos del producto o `None`.  

- **`insert_product(name, description, price)`**  
  - **Propósito:** Insertar un nuevo producto.  
  - **Entradas:** `name`, `description`, `price`.  
  - **Proceso:** `INSERT INTO products (...) VALUES (...)`.  
  - **Salidas:** `True` si éxito, `False` si error.  

- **`delete_product(product_id)`**  
  - **Propósito:** Eliminar un producto.  
  - **Entradas:** `product_id` (int).  
  - **Proceso:** `DELETE FROM products WHERE id = ?`.  
  - **Salidas:** `True` si éxito, `False` si no existe.  

---

### 3.3 `encriptio.py`

*(Ya documentado previamente: encrypt_password, verify_password.)*

---

## 4. Relación con la Base de Datos

Cada función de `database.py` interactúa directamente con las tablas definidas en `db_structure.md`.  
Esto asegura que los endpoints de `app.py` puedan ofrecer la lógica de negocio de forma consistente y segura.

---

## 5. Consideraciones de Seguridad

- **Sesiones:** Actualmente en memoria, se recomienda migrar a JWT o Redis.  
- **Contraseñas:** Siempre cifradas antes de almacenarse.  
- **SQL:** Consultas parametrizadas para evitar inyecciones.  
- **Datos sensibles:** Configuración en `data/conection.json` debe mantenerse fuera del control de versiones.  

---

## 6. Recomendaciones para Colaboradores

- Seguir PEP8 y añadir docstrings en formato Google/NumPy.  
- Implementar tests unitarios para endpoints y funciones críticas.  
- Usar `gunicorn` o `uWSGI` detrás de Nginx para despliegue.  
- Configurar variables de entorno para credenciales y claves secretas.  

---
