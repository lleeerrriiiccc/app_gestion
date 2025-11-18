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

#### `login()`
- **Propósito:** Autenticar a un usuario existente.  
- **Entradas:**  
  - `username` (string, formulario POST).  
  - `password` (string, formulario POST).  
- **Proceso interno:**  
  - Consulta en tabla `users` mediante `database.get_user()`.  
  - Verificación con `encriptio.verify_password()`.  
- **Salidas:**  
  - Redirección a `/dashboard` si es correcto.  
  - Mensaje de error si las credenciales no son válidas.  

#### `register()`
- **Propósito:** Registrar un nuevo usuario.  
- **Entradas:**  
  - `username`, `password`, `email` (strings).  
- **Proceso interno:**  
  - Cifrado de contraseña con `encriptio.encrypt_password()`.  
  - Inserción en tabla `users` mediante `database.insert_user()`.  
- **Salidas:**  
  - Redirección a `/dashboard` si el registro es exitoso.  
  - Error si el usuario ya existe.  

#### `dashboard()`
- **Propósito:** Mostrar información general del sistema.  
- **Entradas:**  
  - Sesión activa del usuario.  
- **Proceso interno:**  
  - Consultas a tablas `users`, `orders`, `invoices`.  
- **Salidas:**  
  - Renderizado de plantilla HTML con datos agregados.  

---

### 3.2 `database.py`

#### `get_user(username)`
- **Propósito:** Recuperar un usuario por nombre.  
- **Entradas:**  
  - `username` (string).  
- **Proceso interno:**  
  - `SELECT * FROM users WHERE username = ?`.  
- **Salidas:**  
  - Diccionario con campos del usuario (`id`, `username`, `password_hash`, `email`).  
  - `None` si no existe.  

#### `insert_user(username, password_hash, email)`
- **Propósito:** Insertar un nuevo usuario.  
- **Entradas:**  
  - `username` (string).  
  - `password_hash` (string).  
  - `email` (string).  
- **Proceso interno:**  
  - `INSERT INTO users (...) VALUES (...)`.  
- **Salidas:**  
  - `True` si la inserción fue exitosa.  
  - `False` si ocurrió un error (ej. duplicado).  

#### `delete_user(user_id)`
- **Propósito:** Eliminar un usuario por ID.  
- **Entradas:**  
  - `user_id` (int).  
- **Proceso interno:**  
  - `DELETE FROM users WHERE id = ?`.  
- **Salidas:**  
  - `True` si se eliminó correctamente.  
  - `False` si no existe.  

*(Se recomienda extender esta sección con todas las funciones definidas en `database.py`, usando la estructura de `db_structure.md` para detallar tablas y columnas implicadas.)*

---

### 3.3 `encriptio.py`

#### `encrypt_password(password)`
- **Propósito:** Generar un hash seguro de la contraseña.  
- **Entradas:**  
  - `password` (string plano).  
- **Proceso interno:**  
  - Uso de algoritmo `bcrypt` o similar.  
- **Salidas:**  
  - `password_hash` (string).  

#### `verify_password(password, password_hash)`
- **Propósito:** Verificar si una contraseña coincide con su hash.  
- **Entradas:**  
  - `password` (string).  
  - `password_hash` (string).  
- **Salidas:**  
  - `True` si coincide.  
  - `False` si no coincide.  

---

## 4. Relación con la Base de Datos

Según `database/db_structure.md`, las tablas principales son:

- **`users`**: Gestión de credenciales y datos de usuario.  
- **`orders`**: Pedidos asociados a usuarios.  
- **`invoices`**: Facturas generadas a partir de pedidos.  
- **`products`**: Catálogo de productos y despieces.  

Cada función en `database.py` interactúa con estas tablas de forma directa, y los endpoints en `app.py` se apoyan en dichas funciones para ofrecer la lógica de negocio.

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
