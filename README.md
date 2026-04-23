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


Dia-23-Abril

💇‍♂️ Parra-Barber - Sistema de Gestión Inteligente
Web profesional para peluquería con reserva de citas avanzada, gestión granular de profesionales y consultoría estética mediante IA.

🚀 Funcionalidades Implementadas
Gestión de Citas Avanzada: Los clientes pueden reservar basándose en la disponibilidad real de cada profesional.

Horarios Granulares: Control independiente para cada peluquero por día de la semana (Lunes a Domingo), permitiendo turnos partidos o mañanas/tardes libres específicas.

Gestión de Festivos: Panel de control para bloquear fechas específicas del calendario (festivos, vacaciones o cierres locales) que se reflejan instantáneamente en la web de reservas.

Panel de Administración (Dashboard): Visualización de citas próximas, gestión de servicios, precios y control total de horarios.

Galería Dinámica: Sistema de visualización de trabajos con optimización de imágenes y paginación.

Seguridad: Autenticación robusta para el administrador con Flask-Login y Bcrypt.

📂 Estructura del Proyecto
/database: Modelos de SQLAlchemy (models.py).

/routes: Lógica de Blueprints (citas.py, admin.py, auth.py).

/templates: Archivos HTML modulares con Jinja2.

/static: Archivos CSS, JS e imágenes optimizadas de la galería.

setup_db.py: Script de inicialización que genera tablas, horarios base (7 días por profesional) y admin.

app.py: Punto de entrada de la aplicación Flask.

🛠️ Configuración e Instalación
Clonar: git clone https://github.com/jcm201080/Peluqueria.git

Entorno virtual: python3 -m venv venv y source venv/bin/activate

Librerías: pip install -r requirements.txt

Inicializar: python setup_db.py (Crea la estructura de horarios independientes y el admin).

Ejecutar: python app.py

🔐 Credenciales Admin (Por defecto)
Teléfono: 633013315

Password: admin123

🚀 Próximos Pasos (Hoja de Ruta)
[ ] Implementación de IA (Asesor Estético): Integrar el motor de OpenAI para responder dudas sobre cortes, barbas y cuidado capilar basándose en los servicios ofrecidos.

[ ] IA de Reservas: Capacitar a la IA para consultar la disponibilidad de la base de datos y sugerir huecos libres a los clientes.

[ ] Integración WhatsApp: Conectar el sistema de citas con la API de WhatsApp para confirmaciones automáticas.