# 💇‍♂️ Web de Gestión - Peluquería IA

Proyecto desarrollado en Python (Flask) para la gestión de citas y asesoría estética mediante IA.

## 🚀 Funcionalidades
- **Gestión de Citas:** Sistema para reservar turnos con dos profesionales distintos.
- **Consultor IA:** Chatbot integrado para dudas sobre estilismo y cuidado capilar.
- **Galería Dinámica:** Visualización de trabajos realizados con paginación automática.
- **Responsive:** Optimizado para móviles.

## 🛠️ Instalación
1. Clonar el repositorio: `git clone https://github.com/jcm201080/Peluqueria.git`
2. Crear entorno virtual: `python3 -m venv venv`
3. Activar entorno: `source venv/bin/activate`
4. Instalar dependencias: `pip install -r requirements.txt`

## 📂 Estructura del Proyecto
- `static/`: Estilos CSS, Imágenes de la galería y Scripts JS.
- `templates/`: Archivos HTML (Jinja2).
- `app.py`: Archivo principal del servidor.
- `models.py`: Definición de la base de datos SQLite.
- `peluqueria.db`: Base de datos local generada automáticamente.

Peluqueria/
├── app.py                # Punto de entrada (inicializa todo)
├── database/             # Carpeta para la persistencia
│   ├── __init__.py
│   └── models.py         # Definición de tablas
├── routes/               # Carpeta de controladores
│   ├── __init__.py
│   ├── citas.py          # Rutas de reservas
│   └── views.py          # Rutas de navegación (index, fotos, etc.)
├── ia/                   # Carpeta para la lógica de IA
│   ├── __init__.py
│   └── consultor.py      # Lógica de OpenAI / Procesamiento
├── static/               # CSS, JS, Imágenes
├── templates/            # HTML
└── requirements.txt


# 💇‍♂️ Parra-Barber - Sistema de Gestión

Web profesional para peluquería con reserva de citas, gestión de profesionales y consultoría por IA.

## 📁 Estructura del Proyecto
- `/database`: Modelos de SQLAlchemy (`models.py`).
- `/routes`: Lógica de Blueprints (`citas.py`, `auth.py`, `admin.py`).
- `/templates`: Archivos HTML con Jinja2.
- `/static`: Estilos CSS y fotos de la galería.
- `setup_db.py`: Script para inicializar la base de datos y el Admin.
- `app.py`: Punto de entrada de la aplicación Flask.

## 🛠️ Configuración Rápida
1. Instalar dependencias: `pip install -r requirements.txt`
2. Configurar DB y Admin: `python setup_db.py`
3. Ejecutar: `python app.py`

## 🔐 Credenciales Admin por defecto
- **Teléfono:** 633013315
- **Password:** admin123

## 🚀 Despliegue en Producción (VPS)
1. Subir cambios: `git push origin main`
2. En el VPS: `git pull`
3. Instalar/Actualizar librerías: `pip install -r requirements.txt`
4. **Inicializar datos:** `python setup_db.py` 
   *(Esto creará las tablas, los peluqueros por defecto y los precios configurados)*.
5. Reiniciar el servicio (Gunicorn/Nginx).

## 🛠️ Tecnologías utilizadas
- **Backend:** Python + Flask
- **DB:** SQLite + SQLAlchemy (ORM)
- **Seguridad:** Flask-Login + Bcrypt (Hashing de contraseñas)
- **Frontend:** HTML5, CSS3 (Diseño Responsive), Jinja2
- **IA:** Consultor estético (en desarrollo)