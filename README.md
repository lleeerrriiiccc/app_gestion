# App Gestión — versión sencilla

Inicia la aplicación Flask localmente (Windows PowerShell):

1. Crear y activar un entorno virtual (opcional pero recomendado):

```powershell
python -m venv .venv; .\.venv\Scripts\Activate.ps1
```

2. Instalar dependencias:

```powershell
pip install -r requirements.txt
```

3. Ejecutar la app:

```powershell
python -m python.app
```

o desde la carpeta `python`:

```powershell
python app.py
```

4. Abrir en el navegador:

http://127.0.0.1:5000/

Notas:
- El proyecto usa `web/html` como plantillas. El login crea una sesión simple en memoria (no persistente).
- La ruta `/register` está protegida por sesión y también se muestra incrustada en el `dashboard`.
- Asegúrate de tener configurado `data/conection.json` con los datos de la base de datos antes de crear usuarios.
