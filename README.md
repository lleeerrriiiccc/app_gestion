# app_gestion — Documentación completa

Este repositorio contiene una aplicación web ligera basada en Flask para gestión de clientes, pedidos, facturas, productos y despieces. El objetivo es proporcionar una interfaz sencilla (HTML + vanilla JS) y una capa de API REST mínima para operaciones CRUD y flujos de asignación.

Contenido de la documentación:
- Resumen y objetivos
- Requisitos y ejecución
- Estructura del proyecto
- Descripción detallada de módulos y funciones
- Endpoints HTTP y contratos API
- Base de datos (resumen y relaciones)
- Plantillas y UX importantes
- Seguridad, pruebas y despliegue

---

## Resumen y objetivos

La aplicación soporta:
- Autenticación (login/logout/registro)
- Gestión de clientes, contactos y direcciones
- Gestión de pedidos y sus líneas
- Gestión de productos y piezas (despiece)
- Subida y visualización de facturas y planos
- Asignaciones de procesos a empleados y máquinas

Diseño: servidor Flask que sirve plantillas HTML estáticas en `web/html` y expone APIs bajo `/api/*` para que los scripts client-side realicen acciones.

---

## Requisitos y ejecución

Requisitos básicos:
- Python 3.8+
- Dependencias listadas en `requirements.txt` (Flask, mysql-connector-python o mysqlclient, flask-cors, werkzeug, ...)

Arrancar en desarrollo (PowerShell, desde la raíz del repo):

```powershell
python .\python\app.py
```

La app corre por defecto en `0.0.0.0:80` con `debug=True` en `app.py` — cambiar en producción.

Archivo de conexión a la DB: `data/conection.json`.

---

## Estructura del proyecto (resumen)

- `python/` : código servidor (app.py, database.py, encription.py, helpers)
- `web/html/` : plantillas HTML organizadas por módulo (`productos`, `pedidos`, `clientes`, `users`, `facturas`, ...)
- `web/css/` : estilo principal `main.css`
- `files/` : uploads (facturas, planos)
- `data/` : configuración local (`conection.json`, `exclusions.json`)
- `database/` : documentación / generadores (ej. `db_structure.md`, `generate_docs.py`)

---

## Módulos principales y funciones

Se exponen aquí las responsabilidades principales y un resumen de las funciones más relevantes. Para código detallado, revisar `python/app.py` y `python/database.py`.

### `python/app.py` (Flask app)

Responsabilidad: definir rutas que sirven plantillas y endpoints JSON, controlar sesiones y validar parámetros.

Rutas / endpoints importantes (resumen):
- `/login` (GET, POST): pagina de login / autenticación.
- `/logout`: limpia sesión.
- `/dashboard`: página principal tras login.
- `/products`, `/products/add`, `/products/detail`: gestión de productos y formulario de despiece.
- `/piezas/list` : nueva página para listar piezas agrupadas por producto.
- `/pedidos`, `/pedidos/add`, `/pedidos/detalles`, `/pedidos/assign`, `/pedidos/assignment_detail`, `/pedidos/delete`: gestión de pedidos y flujo de asignación.
- `/api/products?q=`: devuelve productos (usa `db.products_list`).
- `/api/piezas?name=&code=`: devuelve piezas filtradas (usa `db.list_piezas`).
- `/api/producto/piezas?id=`: devuelve piezas de un producto (usa `db.get_piezas_by_producto`).
- `/api/pedidos`, `/api/pedidos/<id>/lines`: listados y líneas de pedidos.
- `/api/pedidos/assign`: crea/actualiza asignaciones por línea/proceso.
- `/api/pedidos/assigned`: devuelve asignaciones de un pedido (usa `db.get_assignments_for_pedido`).
- `/api/maquinas`, `/api/processes`: listas de máquinas y procesos.

Notas:
- Muchas rutas aceptan tanto `form` como JSON (`request.get_json(silent=True)`), lo que facilita llamadas desde fetch() en el frontend.
- Rutas estáticas para servir archivos: `/css/*`, `/img/*`, y `/pdf/planos/...`.

### `python/database.py` (capa de datos)

Responsabilidad: conexión a MySQL, helpers read/write y funciones específicas para cada entidad.

Funciones esenciales (resumen y comportamiento esperado):

- `connect()` : lee `data/conection.json` y devuelve conexión mysql.connector.
- `read_data(query, params=None)` : ejecuta SELECT y devuelve lista de diccionarios (cursor dictionary=True).
- `write_data(query, params=None)`, `update_data(query, data)`, `delete_data(query, data)` : helpers genéricos para modificación.

- Usuarios / autenticación
  - `check_username(username)` : comprueba existencia de username.
  - `create_user(username, password, privilege=0)` : inserta usuario (password ya debe estar hasheada en app.py).
  - `get_users(username=None, dept=None)` : devuelve usuarios, soporta filtros.
  - `privileges(username)` / `check_privilege(required, user)` : lectura de privilegios.

- Clientes y contactos
  - `clients_info(client="*")` : lista clientes (o busca por nombre parcial)
  - `add_client(name, nif)` : inserta cliente (intenta campos `email`/`nif` según esquema)
  - `contact_info(id)`, `addresses_info(client_id)` : devuelve contactos y direcciones
  - `add_contact`, `update_contact`, `delete_contact`
  - `add_address`, `update_address`, `delete_address`

- Facturas
  - `upload_invoice(client, file_path, email, checkbox)` : inserta factura y guarda path
  - `delete_invoice(id)`

- Pedidos y líneas
  - `add_pedido(cliente_id, direccion_envio)` : crea pedido y devuelve id
  - `add_linea_pedido(pedido_id, producto_id, cantidad)` : añade línea
  - `get_pedido(pedido_id)` : devuelve datos del pedido (cliente, fecha_taller, estado)
  - `get_pedido_lines(pedido_id)` : devuelve líneas con información de producto (idlinia, producto_nombre, cantidad, etc.)
  - `list_pedidos(cliente_id=None, date_from=None, date_to=None)` : listados con filtros

- Productos y piezas (despiece)
  - `products_list(q='*', idproducto=None)` : busca productos por nombre/código o por id
  - `create_product(nombre, codigo, descripcion, precio, planos)` : inserta producto
  - `create_pieza(name, codigo=None, plano=None)` : inserta pieza
  - `add_despiece(producto_id, pieza_id)` : crea relación producto↔pieza
  - `get_piezas_by_producto(producto_id)` : devuelve piezas ligadas a un producto (idpiezas, name, codigo, plano)
  - `list_piezas(name=None, code=None)` : devuelve piezas filtradas (incluye datos de producto cuando se filtra por name/code)

- Asignaciones (assignaciones)
  - `add_assignment(pedido, empleado, proceso, idlinia)` : inserta asignación
  - `get_assignments_for_user(username)` : lista asignaciones para usuario
  - `update_assignment(pedido, empleado, proceso, idlinia, maquina=None, estado=None)` : actualiza asignación existente
  - `get_assignments_for_pedido(pedido_id)` : devuelve asignaciones de un pedido (empleado id, maquina id, idlinia, proceso, estado)
  - `pedido_assigned(pedido_id, proceso, idlinia)` : helper para determinar si línea/proceso ya está asignado

Observaciones:
- `list_piezas` en el repositorio devuelve diferentes conjuntos de campos según los parámetros (`name`/`code`), por lo que el frontend espera campos como `idpiezas`, `nombre_pieza`, `codigo_pieza`, `idproducto`, `nombre_producto`.

---

## Contratos de API (resumen práctico)

Estos son los endpoints que el frontend ya usa y el formato que espera:

- `GET /api/products?q=<texto>`
  - Devuelve: array de productos [{idproducto, nombre, descripcion, codigo, precio, planos}, ...]

- `GET /api/producto/piezas?id=<idproducto>`
  - Devuelve: array de piezas del producto [{idpiezas, name, codigo, plano}, ...]

- `GET /api/piezas?name=<texto>&code=<texto>`
  - Devuelve: array de piezas con campos cuando se filtra por name/code: `idpiezas`, `nombre_pieza`, `codigo_pieza`, `idproducto`, `nombre_producto`, `codigo_producto`

- `GET /api/pedidos?client_id=&date_from=&date_to=`
  - Devuelve: array de pedidos (idpedido, cliente, direccion_envio, fecha_taller, estado, cliente_id)

- `GET /api/pedidos/<id>/lines` o `GET /api/pedido?id=` (ambos usados)
  - Devuelve: líneas de pedido con `idlinia`, `producto`, `producto_nombre`, `cantidad`, etc.

- `POST /api/pedidos/assign` (JSON)
  - Input: { pedido, idlinia, proceso, empleado, maquina? }
  - Crea o actualiza asignación. Devuelve 201/200 o error.

- `POST /api/pedidos/assigned` (JSON o form)
  - Input: { pedido } o form field `pedido`
  - Devuelve: array de assignaciones para el pedido (se espera `idlinia`, `proceso`/`idproceso`, `maquina`/`maquina_id`, `estado`, `empleado` (id), y opcional `empleado_user` para mostrar nombre en UI).

---

## Plantillas y UX relevantes

- `web/html/productos/piezas/piezas_list.html` (añadida): lista piezas agrupadas por producto; filtros:
  - `product-search` (autocomplete `/api/products?q=`)
  - `filter-code` (autocomplete `/api/piezas?code=`)
  - `filter-name` (busca por nombre de pieza, filtrado cliente-side)
  - Botón `Cargar todas` para recuperar todas las piezas (consumo pesado, por precaución)
  - Comportamiento interacciones: seleccionar producto auto-puebla sugerencias de códigos (y viceversa) para facilitar filtrado.

---

## Base de datos (resumen)

La estructura completa está en `database/db_structure.md`. Resumen de tablas claves:
- `clientes`, `datos_contacto`, `datos_envio`
- `producto`, `piezas`, `despiece_productos`
- `pedidos`, `linias_pedido`, `assignaciones`
- `maquinas`, `procesos`, `facturas`, `users`, `departamentos`

Relaciones principales:
- `despiece_productos.producto` → `producto.idproducto`
- `despiece_productos.pieza` → `piezas.idpiezas`
- `linias_pedido.producto` → `producto.idproducto`
- `assignaciones.pedido` → `pedidos.idpedido`
- `assignaciones.empleado` → `users.id`

---

## Seguridad y recomendaciones

- No usar `debug=True` en producción.
- Mover `app.secret_key` a variable de entorno y usar sesiones seguras (cookie flags ya configuradas parcialmente).
- Migrar almacenamiento de sesiones a Redis si la aplicación va a escalar.
- Asegurar backups de la DB y de la carpeta `files/` donde se guardan uploads.
- Limitar `Cargar todas` en la UI y paginar resultados en endpoints que puedan devolver muchos registros.

---

## Testing y QA

- Añadir pruebas unitarias para `python/database.py` y pruebas de integración/instrumentación para `/api/*`.
- Para pruebas locales: crear una base de datos de desarrollo con las mismas tablas y unos datos de ejemplo.

---

## Despliegue

- Recomendación de producción: ejecutar Flask con `gunicorn` y detrás de Nginx en un servidor Linux.
- Variables de entorno: `FLASK_SECRET`, configuración de DB en `data/conection.json` (o preferible: variables de entorno o un vault).

---

## Próximos pasos y mejoras sugeridas

1. Añadir paginación a `GET /api/products` y `GET /api/piezas`.
2. Añadir pruebas automáticas (pytest) y pipeline CI.
3. Mejorar UX del autocomplete con navegación por teclado.
4. Añadir controles de autorización más finos para rutas sensibles (roles/privilegios por acción).
