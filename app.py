import os
from flask import Flask, render_template, request, redirect, url_for, flash
from database.models import db, Usuario, Peluquero, Servicio, Cita
from flask_login import LoginManager, current_user
from flask_bcrypt import Bcrypt
from routes.admin import admin_bp
from routes.auth import auth_bp
from routes.ia_routes import ia_bp
from routes.views import views_bp
from routes.citas import citas_bp
from datetime import datetime, timedelta
import json
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)

app.config['SECRET_KEY'] = 'clave_secreta_muy_dificil_123'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///peluqueria.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['MAX_CONTENT_LENGTH'] = 20 * 1024 * 1024

# Inicialización de extensiones
db.init_app(app)
bcrypt = Bcrypt(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'auth.login'

@login_manager.user_loader
def load_user(user_id):
    return Usuario.query.get(int(user_id))

# Registro de Blueprints
app.register_blueprint(admin_bp)
app.register_blueprint(auth_bp)
app.register_blueprint(ia_bp)
app.register_blueprint(views_bp)
app.register_blueprint(citas_bp) # El Blueprint de citas gestionará /contacto

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/servicios')
def servicios():
    lista_servicios = Servicio.query.all()
    return render_template('servicios.html', servicios=lista_servicios)

@app.route('/fotos')
def fotos():
    folder = os.path.join(app.static_folder, "img/fotos")
    if not os.path.exists(folder):
        return "Carpeta de fotos no encontrada", 404
    archivos = [f for f in os.listdir(folder) if f.endswith(('png', 'jpg', 'jpeg', 'gif'))]
    def extraer_numero(nombre_archivo):
        nombre_sin_ext = nombre_archivo.rsplit('.', 1)[0]
        try: return int(nombre_sin_ext)
        except ValueError: return 0
    archivos.sort(key=extraer_numero, reverse=True) 
    imagenes = [f"img/fotos/{img}" for img in archivos]
    page = request.args.get('page', 1, type=int)
    per_page = 20
    total_pages = (len(imagenes) + per_page - 1) // per_page
    start = (page - 1) * per_page
    end = start + per_page
    imagenes_pagina = imagenes[start:end]
    return render_template('fotos.html', imagenes=imagenes_pagina, page=page, total_pages=total_pages)

@app.context_processor
def inject_config():
    try:
        with open('config_web.json', 'r', encoding='utf-8') as f:
            config = json.load(f)
    except Exception:
        config = {"nombre_negocio": "Parra-Barber", "color_principal": "#d4a373", "color_fondo": "#1a1a1a"}
    return dict(web=config)

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port, debug=True)