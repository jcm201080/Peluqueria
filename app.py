import os
from flask import Flask, render_template, request
from database.models import db, Usuario, Peluquero, Servicio, Cita
from flask_login import LoginManager, current_user
from flask_bcrypt import Bcrypt
from routes.admin import admin_bp
from routes.auth import auth_bp

from datetime import datetime, timedelta

from routes.citas import citas_bp

import json






# 1. Definimos la App primero
app = Flask(__name__)

# 2. Configuraciones necesarias
app.config['SECRET_KEY'] = 'clave_secreta_muy_dificil_123' # ¡Añadido!
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///peluqueria.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['MAX_CONTENT_LENGTH'] = 20 * 1024 * 1024  # Límite de 20MB

app.register_blueprint(admin_bp)
app.register_blueprint(auth_bp)


# 3. Inicializamos extensiones con la app ya creada
db.init_app(app)
bcrypt = Bcrypt(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'auth.login'

@login_manager.user_loader
def load_user(user_id):
    return Usuario.query.get(int(user_id))

# --- RUTAS ---

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

    # 1. Leemos los archivos
    archivos = [f for f in os.listdir(folder) if f.endswith(('png', 'jpg', 'jpeg', 'gif'))]
    
    # 2. ORDEN NUMÉRICO: Intentamos convertir el nombre a entero para ordenar
    # Si el nombre no es un número (ej: "logo.png"), lo mandamos al final (0)
    def extraer_numero(nombre_archivo):
        nombre_sin_ext = nombre_archivo.rsplit('.', 1)[0]
        try:
            return int(nombre_sin_ext)
        except ValueError:
            return 0

    archivos.sort(key=extraer_numero, reverse=True) 
    
    # 3. Construimos las rutas usando la lista ya ORDENADA NUMÉRICAMENTE
    imagenes = [f"img/fotos/{img}" for img in archivos]
    
    # 4. Paginación (igual que antes)
    page = request.args.get('page', 1, type=int)
    per_page = 20
    total_pages = (len(imagenes) + per_page - 1) // per_page
    start = (page - 1) * per_page
    end = start + per_page
    imagenes_pagina = imagenes[start:end]

    return render_template('fotos.html', imagenes=imagenes_pagina, page=page, total_pages=total_pages)


# app.py (o donde tengas la ruta /contacto)
@app.route('/contacto')
def contacto():
    servicios = Servicio.query.all()
    
    # 1. BUSCAR PRÓXIMA CITA DEL USUARIO
    proxima_cita = None
    if current_user.is_authenticated:
        # Buscamos la cita más cercana (hoy o en el futuro)
        proxima_cita = Cita.query.filter(
            Cita.usuario_id == current_user.id,
            Cita.fecha >= datetime.now().date()
        ).order_by(Cita.fecha.asc(), Cita.hora.asc()).first()

    # --- Tu lógica de días (se mantiene igual, está muy bien) ---
    dias_es = ["Lunes", "Martes", "Miércoles", "Jueves", "Viernes", "Sábado", "Domingo"]
    meses_es = ["Ene", "Feb", "Mar", "Abr", "May", "Jun", "Jul", "Ago", "Sep", "Oct", "Nov", "Dic"]
    dias_disponibles = []
    for i in range(12):
        fecha = datetime.now() + timedelta(days=i)
        if fecha.weekday() == 6: continue
        dias_disponibles.append({
            'valor': fecha.strftime('%Y-%m-%d'),
            'texto': f"{dias_es[fecha.weekday()]}, {fecha.day} {meses_es[fecha.month - 1]}"
        })
        if len(dias_disponibles) == 10: break
    
    # IMPORTANTE: Pasamos 'proxima_cita' al template
    return render_template('contacto.html', 
                           servicios=servicios, 
                           dias=dias_disponibles, 
                           proxima_cita=proxima_cita)

# contacto con wasap por ahora dejamos sin wasap (Nos mandan un wasap para confirmar)
# @citas_bp.route('/reservar', methods=['POST'])

# def reservar():

#     fecha_str = request.form.get('fecha')

#     hora_str = request.form.get('hora')

#     servicio = request.form.get('servicio')

#     peluquero_id_manual = request.form.get('peluquero_id')



#     # Lógica de identificación de usuario (se mantiene intacta)

#     if current_user.is_authenticated and current_user.es_admin and request.form.get('nombre'):

#         nombre = f"Admin: {request.form.get('nombre')}"

#         telefono = request.form.get('telefono', 'S/N')

#         usuario_id = None

#     elif current_user.is_authenticated:

#         nombre = current_user.nombre

#         telefono = current_user.telefono

#         usuario_id = current_user.id

#     else:

#         nombre = request.form.get('nombre')

#         telefono = request.form.get('telefono')

#         usuario_id = None



#     # Usamos un solo bloque try-except general para cazar cualquier error

#     try:

#         fecha_obj = datetime.strptime(fecha_str, '%Y-%m-%d').date()

#         hora_obj = datetime.strptime(hora_str[:5], '%H:%M').time()

#         dia_semana_int = fecha_obj.weekday()



#         peluquero_asignado_id = None



#         # Si el admin elige uno, verificamos disponibilidad rápida

#         if peluquero_id_manual:

#             peluquero_asignado_id = int(peluquero_id_manual)

#         else:

#             # Búsqueda automática de peluquero disponible

#             peluqueros = Peluquero.query.filter_by(activo=True).all()

#             for p in peluqueros:

#                 horario_dia = HorarioPeluquero.query.filter_by(

#                     peluquero_id=p.id,

#                     dia_semana=dia_semana_int

#                 ).first()



#                 if horario_dia and horario_dia.trabaja:

#                     # Comprobar si la hora cae en sus turnos

#                     h_im = datetime.strptime(horario_dia.h_inicio_m, '%H:%M').time()

#                     h_fm = datetime.strptime(horario_dia.h_fin_m, '%H:%M').time()

#                     h_it = datetime.strptime(horario_dia.h_inicio_t, '%H:%M').time()

#                     h_ft = datetime.strptime(horario_dia.h_fin_t, '%H:%M').time()



#                     esta_en_horario = (h_im <= hora_obj < h_fm) or (h_it <= hora_obj < h_ft)

                   

#                     if esta_en_horario:

#                         ocupada = Cita.query.filter_by(fecha=fecha_obj, hora=hora_obj, peluquero_id=p.id).first()

#                         if not ocupada:

#                             peluquero_asignado_id = p.id

#                             break



#         # Si encontramos un peluquero disponible

#         if peluquero_asignado_id:

#             nueva_cita = Cita(

#                 fecha=fecha_obj,

#                 hora=hora_obj,

#                 peluquero_id=peluquero_asignado_id,

#                 servicio=servicio if servicio else "Reserva Manual",

#                 usuario_id=usuario_id,

#                 nombre_invitado=nombre if not usuario_id else None,

#                 telefono_cliente=telefono

#             )

#             db.session.add(nueva_cita)

#             db.session.commit()

           

#             # --- LÓGICA DE WHATSAPP ---

#             # Si el que reserva NO es el admin, lo mandamos a WhatsApp

#             if not (current_user.is_authenticated and current_user.es_admin):

#                 telefono_negocio = "34633013315" # Tu número con prefijo

#                 fecha_bonita = fecha_obj.strftime('%d/%m/%Y')

#                 hora_bonita = hora_obj.strftime('%H:%M')

               

#                 texto = (f"¡Hola Parra-Barber! 👋\n"

#                          f"He reservado una cita:\n"

#                          f"👤 *Nombre:* {nombre}\n"

#                          f"✂️ *Servicio:* {servicio}\n"

#                          f"📅 *Día:* {fecha_bonita}\n"

#                          f"⏰ *Hora:* {hora_bonita}\n"

#                          f"¿Me confirmas la cita?")

               

#                 # Codificamos el texto para URL

#                 mensaje_url = urllib.parse.quote(texto)

#                 whatsapp_url = f"https://api.whatsapp.com/send?phone={telefono_negocio}&text={mensaje_url}"

               

#                 # Usamos una categoría de flash específica si quieres darle estilo en HTML

#                 flash("✅ ¡Cita guardada! Redirigiendo a WhatsApp para confirmar...", "success")

#                 return redirect(whatsapp_url)

           

#             else:

#                 # Si es el ADMIN quien reserva desde su panel

#                 flash(f"✅ Cita confirmada para {nombre}", "success")

#                 return redirect(url_for('admin.gestion_diaria', fecha_busqueda=fecha_str))



#         else:

#             # Si el bucle termina y peluquero_asignado_id sigue siendo None

#             flash("Lo sentimos, no hay hueco disponible con ese profesional en este horario.", "error")

#             return redirect(url_for('contacto'))



#     except Exception as e:

#         # Si algo falla en la base de datos o al transformar la fecha

#         db.session.rollback()

#         flash(f"Error al reservar: {e}", "error")

#         return redirect(url_for('contacto'))

@app.context_processor
def inject_config():
    try:
        with open('config_web.json', 'r', encoding='utf-8') as f:
            config = json.load(f)
    except Exception:
        # Valores por defecto si el archivo falla
        config = {
            "nombre_negocio": "Parra-Barber", 
            "color_principal": "#d4a373",
            "color_fondo": "#1a1a1a"
        }
    return dict(web=config)

# 4. Registro de Blueprints
app.register_blueprint(citas_bp)
# No olvides registrar el de auth cuando lo crees:
# from routes.auth import auth_bp
# app.register_blueprint(auth_bp)

if __name__ == '__main__':
    with app.app_context():
        db.create_all() # Crea la base de datos y las tablas automáticamente
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port, debug=True)