import os
from flask import Blueprint, render_template, redirect, url_for, request, flash
from flask_login import login_required, current_user
from database.models import db, Cita, Peluquero, Servicio, Configuracion
from werkzeug.utils import secure_filename
from PIL import Image
import time # Añade este import

admin_bp = Blueprint('admin', __name__, url_prefix='/admin')

UPLOAD_FOLDER = 'static/img/fotos'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

@admin_bp.route('/dashboard')
@login_required
def dashboard():
    if not current_user.es_admin:
        return "Acceso Denegado: No tienes permisos de administrador.", 403
    
    # Obtenemos todos los datos necesarios para las secciones del dashboard
    todas_citas = Cita.query.order_by(Cita.fecha, Cita.hora).all()
    lista_peluqueros = Peluquero.query.all()
    lista_servicios = Servicio.query.all()
    # Obtenemos la primera fila de configuración (la única que debería existir)
    config = Configuracion.query.first()
    
    return render_template('admin/dashboard.html', 
                           citas=todas_citas, 
                           peluqueros=lista_peluqueros,
                           servicios=lista_servicios,
                           config=config)

# --- GESTIÓN DE CITAS ---

@admin_bp.route('/cita/eliminar/<int:id>')
@login_required
def eliminar_cita(id):
    cita = Cita.query.get_or_404(id)
    db.session.delete(cita)
    db.session.commit()
    flash("Cita eliminada correctamente.")
    return redirect(url_for('admin.dashboard'))

# --- GESTIÓN DE SERVICIOS ---

@admin_bp.route('/servicio/nuevo', methods=['POST'])
@login_required
def nuevo_servicio():
    nombre = request.form.get('nombre')
    precio = request.form.get('precio')
    
    if nombre and precio:
        nuevo = Servicio(nombre=nombre, precio=float(precio))
        db.session.add(nuevo)
        db.session.commit()
        flash(f"Servicio '{nombre}' añadido.")
    return redirect(url_for('admin.dashboard'))

@admin_bp.route('/servicio/eliminar/<int:id>')
@login_required
def eliminar_servicio(id):
    serv = Servicio.query.get_or_404(id)
    db.session.delete(serv)
    db.session.commit()
    flash("Servicio eliminado.")
    return redirect(url_for('admin.dashboard'))

# --- GESTIÓN DE HORARIOS ---

@admin_bp.route('/horarios/actualizar', methods=['POST'])
@login_required
def actualizar_horarios():
    config = Configuracion.query.first()
    if not config:
        config = Configuracion()
        db.session.add(config)
    
    config.h_inicio_manana = request.form.get('h_im')
    config.h_fin_manana = request.form.get('h_fm')
    config.h_inicio_tarde = request.form.get('h_it')
    config.h_fin_tarde = request.form.get('h_ft')
    
    db.session.commit()
    flash("Horarios actualizados correctamente.")
    return redirect(url_for('admin.dashboard'))


# --- GESTIÓN DE SERVICIOS (MODIFICAR) ---

@admin_bp.route('/servicio/editar/<int:id>', methods=['POST'])
@login_required
def editar_servicio(id):
    servicio = Servicio.query.get_or_404(id)
    servicio.nombre = request.form.get('nombre')
    servicio.precio = float(request.form.get('precio'))
    db.session.commit()
    flash(f"Servicio '{servicio.nombre}' modificado correctamente.")
    return redirect(url_for('admin.dashboard'))

# --- GESTIÓN DE HORARIOS POR PELUQUERO ---

@admin_bp.route('/peluquero/horario/<int:id>', methods=['POST'])
@login_required
def actualizar_horario_peluquero(id):
    p = Peluquero.query.get_or_404(id)
    p.h_inicio_manana = request.form.get('h_im')
    p.h_fin_manana = request.form.get('h_fm')
    p.h_inicio_tarde = request.form.get('h_it')
    p.h_fin_tarde = request.form.get('h_ft')
    p.dias_laborables = ",".join(request.form.getlist('dias'))
    
    db.session.commit()
    flash(f"Horario de {p.nombre} actualizado.")
    return redirect(url_for('admin.dashboard'))

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS



@admin_bp.route('/admin/borrar-foto', methods=['POST'])
@login_required
def borrar_foto():
    if not current_user.es_admin:
        return "Acceso denegado", 403
    
    nombre_archivo = request.form.get('nombre_archivo')
    # Eliminamos el prefijo 'img/fotos/' si viene incluido
    clean_name = nombre_archivo.split('/')[-1]
    ruta_completa = os.path.join(UPLOAD_FOLDER, clean_name)
    
    if os.path.exists(ruta_completa):
        os.remove(ruta_completa)
        flash('Foto eliminada')
    
    return redirect(url_for('fotos'))


@admin_bp.route('/admin/subir-foto', methods=['POST'])
@login_required
def subir_foto():
    # 1. Seguridad: Solo el admin entra aquí
    if not current_user.es_admin:
        return "Acceso denegado", 403
    
    # 2. Validación: ¿Hay un archivo?
    if 'foto' not in request.files:
        flash('No se seleccionó ningún archivo')
        return redirect(request.referrer)
    
    file = request.files['foto']
    
    if file.filename == '':
        flash('Nombre de archivo no válido')
        return redirect(request.referrer)

    if file and allowed_file(file.filename):
        # --- LÓGICA DE NOMBRE PARA ORDENACIÓN ---
        # Extraemos la extensión (.jpg, .png...)
        ext = file.filename.rsplit('.', 1)[1].lower()
        # El nombre será el tiempo actual en segundos (ej: 1713800000.jpg)
        # Esto garantiza que la última subida tenga el número más alto
        nombre_ordenado = f"{int(time.time())}.{ext}"
        
        # Asegurar que la carpeta existe
        if not os.path.exists(UPLOAD_FOLDER):
            os.makedirs(UPLOAD_FOLDER)
        
        filepath = os.path.join(UPLOAD_FOLDER, nombre_ordenado)

        try:
            # --- OPTIMIZACIÓN CON PILLOW ---
            img = Image.open(file)
            
            # Corregir orientación si la foto viene de un móvil (EXIF)
            try:
                from PIL import ImageOps
                img = ImageOps.exif_transpose(img)
            except:
                pass

            if img.mode in ("RGBA", "P"):
                img = img.convert("RGB")
            
            # Redimensión nítida (LANCZOS)
            img.thumbnail((1200, 1200), Image.Resampling.LANCZOS)
            
            # Guardar optimizada
            img.save(filepath, optimize=True, quality=85)

            flash('✅ Trabajo añadido al principio de la galería')
        except Exception as e:
            flash(f'❌ Error al procesar la imagen: {str(e)}')
            return redirect(request.referrer)
    
    return redirect(url_for('fotos'))


@admin_bp.route('/admin/renombrar-foto', methods=['POST'])
@login_required
def renombrar_foto():
    if not current_user.es_admin:
        return "Acceso denegado", 403
    
    # Recogemos los datos del formulario
    # imagen viene como 'img/fotos/12345.jpg'
    ruta_relativa = request.form.get('nombre_actual') 
    nuevo_orden = request.form.get('nuevo_orden')
    
    if not nuevo_orden or not ruta_relativa:
        flash("Datos insuficientes")
        return redirect(url_for('fotos'))

    # Limpiamos el nombre para obtener solo el archivo (ej: 12345.jpg)
    nombre_actual = ruta_relativa.split('/')[-1]
    ext = nombre_actual.rsplit('.', 1)[1].lower()
    
    # Construimos las rutas absolutas
    # Asegúrate de que UPLOAD_FOLDER esté definido arriba en tu archivo
    vieja_ruta = os.path.join(UPLOAD_FOLDER, nombre_actual)
    nuevo_nombre = f"{nuevo_orden}.{ext}"
    nueva_ruta = os.path.join(UPLOAD_FOLDER, nuevo_nombre)
    if os.path.exists(nueva_ruta):
        # Opción A: No dejar que pase
        flash(f"⚠️ El número {nuevo_orden} ya está en uso. Usa otro para no borrar la otra foto.")
        return redirect(url_for('fotos'))
    
    try:
        # Si ya existe una foto con ese número, Python dará error o la sobrescribirá.
        # Por seguridad, comprobamos:
        if os.path.exists(nueva_ruta):
            flash(f"⚠️ Ya existe una foto con la prioridad {nuevo_orden}. Elige otro número.")
        else:
            os.rename(vieja_ruta, nueva_ruta)
            flash(f"✅ Foto movida a posición {nuevo_orden}")
    except Exception as e:
        flash(f"❌ Error al renombrar: {str(e)}")
    
    return redirect(url_for('fotos'))