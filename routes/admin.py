import os
from flask import Blueprint, render_template, redirect, url_for, request, flash
from flask_login import login_required, current_user
from database.models import db, Cita, Peluquero, Servicio, Configuracion, HorarioPeluquero, ExcepcionHorario
# Asegúrate de que ExcepcionHorario esté en esa lista ↑
from werkzeug.utils import secure_filename
from PIL import Image
import time # Añade este import
from datetime import datetime
from routes.citas import generar_franjas

admin_bp = Blueprint('admin', __name__, url_prefix='/admin')

UPLOAD_FOLDER = 'static/img/fotos'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

@admin_bp.route('/dashboard')
@login_required
def index():
    if not current_user.es_admin:
        return "Acceso Denegado", 403
    
    tab = request.args.get('tab', 'citas')
    fecha_busqueda = request.args.get('fecha_busqueda')
    
    # 1. Lógica para la TABLA DE CITAS
    if fecha_busqueda:
        fecha_obj = datetime.strptime(fecha_busqueda, '%Y-%m-%d').date()
        citas_para_mostrar = Cita.query.filter_by(fecha=fecha_obj).order_by(Cita.hora).all()
        fecha_para_input = fecha_busqueda
    else:
        citas_para_mostrar = Cita.query.filter(Cita.fecha >= datetime.now().date()).order_by(Cita.fecha, Cita.hora).all()
        fecha_para_input = datetime.now().strftime('%Y-%m-%d')

    # 2. Lógica para el resto de pestañas
    lista_peluqueros = Peluquero.query.all()
    lista_servicios = Servicio.query.all()

    # --- NUEVA LÓGICA PARA FESTIVOS ---
    # Traemos los festivos de hoy en adelante para que aparezcan en la tabla
    lista_festivos = ExcepcionHorario.query.filter(ExcepcionHorario.fecha >= datetime.now().date()).order_by(ExcepcionHorario.fecha).all()
    
    return render_template('admin/dashboard.html', 
                           citas=citas_para_mostrar, 
                           peluqueros=lista_peluqueros,
                           servicios=lista_servicios,
                           festivos=lista_festivos,  # <--- IMPORTANTE: Pasamos la lista aquí
                           fecha_actual=fecha_para_input,
                           active_tab=tab)

# --- GESTIÓN DE CITAS ---

@admin_bp.route('/cita/eliminar/<int:id>')
@login_required
def eliminar_cita(id):
    cita = Cita.query.get_or_404(id)
    db.session.delete(cita)
    db.session.commit()
    flash("Cita eliminada correctamente.")
    return redirect(url_for('admin.index'))

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
    return redirect(url_for('admin.index'))

@admin_bp.route('/servicio/eliminar/<int:id>')
@login_required
def eliminar_servicio(id):
    serv = Servicio.query.get_or_404(id)
    db.session.delete(serv)
    db.session.commit()
    flash("Servicio eliminado.")
    return redirect(url_for('admin.index'))

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
    return redirect(url_for('admin.index'))


# --- GESTIÓN DE SERVICIOS (MODIFICAR) ---

@admin_bp.route('/servicio/editar/<int:id>', methods=['POST'])
@login_required
def editar_servicio(id):
    servicio = Servicio.query.get_or_404(id)
    servicio.nombre = request.form.get('nombre')
    servicio.precio = float(request.form.get('precio'))
    db.session.commit()
    flash(f"Servicio '{servicio.nombre}' modificado correctamente.")
    return redirect(url_for('admin.index'))

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
    return redirect(url_for('admin.index'))

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


@admin_bp.route('/admin/gestion-diaria')
@login_required
def gestion_diaria():
    if not current_user.es_admin:
        return redirect(url_for('index'))

    fecha_str = request.args.get('fecha_busqueda', datetime.now().strftime('%Y-%m-%d'))
    fecha_obj = datetime.strptime(fecha_str, '%Y-%m-%d').date()
    dia_semana_int = fecha_obj.weekday()

    # 1. Obtener citas ya existentes para ese día
    citas = Cita.query.filter_by(fecha=fecha_obj).order_by(Cita.hora).all()

    # 2. Calcular huecos libres usando la NUEVA estructura de HorarioPeluquero
    peluqueros = Peluquero.query.filter_by(activo=True).all()
    huecos_detalles = {} # { '10:00': [p1, p2], '10:30': [p1] }

    for p in peluqueros:
        # Buscamos el horario de este peluquero para el día de la semana actual
        # Aquí es donde fallaba antes al buscar 'dias_laborables'
        from database.models import HorarioPeluquero # Asegúrate de importar esto arriba
        horario = HorarioPeluquero.query.filter_by(peluquero_id=p.id, dia_semana=dia_semana_int).first()

        if horario and horario.trabaja:
            from routes.citas import generar_franjas
            franjas = generar_franjas(horario.h_inicio_m, horario.h_fin_m) + \
                      generar_franjas(horario.h_inicio_t, horario.h_fin_t)

            for hora_f in franjas:
                # Comprobar si ya tiene una cita a esa hora
                hora_cita_obj = datetime.strptime(hora_f, '%H:%M').time()
                ocupado = Cita.query.filter_by(fecha=fecha_obj, hora=hora_cita_obj, peluquero_id=p.id).first()
                
                if not ocupado:
                    if hora_f not in huecos_detalles:
                        huecos_detalles[hora_f] = []
                    huecos_detalles[hora_f].append(p)

    horas_libres = sorted(huecos_detalles.keys())

    return render_template('admin/gestion_citas.html', 
                           citas=citas, 
                           horas_libres=horas_libres, 
                           huecos_detalles=huecos_detalles,
                           fecha_actual=fecha_str)


@admin_bp.route('/actualizar_horario_detallado/<int:id>', methods=['POST'])
@login_required
def actualizar_horario_detallado(id):
    if not current_user.es_admin:
        return redirect(url_for('index'))
    
    peluquero = Peluquero.query.get_or_404(id)
    
    for h in peluquero.horarios:
        # Recuperamos los datos del form para cada día
        h.trabaja = True if request.form.get(f'trabaja_{h.dia_semana}') else False
        h.h_inicio_m = request.form.get(f'h_im_{h.dia_semana}')
        h.h_fin_m = request.form.get(f'h_fm_{h.dia_semana}')
        h.h_inicio_t = request.form.get(f'h_it_{h.dia_semana}')
        h.h_fin_t = request.form.get(f'h_ft_{h.dia_semana}')
    
    db.session.commit()
    flash(f"Horario de {peluquero.nombre} actualizado correctamente.")
    return redirect(url_for('admin.index', tab='horarios'))

@admin_bp.route('/añadir_festivo', methods=['POST'])
@login_required
def añadir_festivo():
    # Lógica para guardar en la tabla ExcepcionHorario
    fecha_str = request.form.get('fecha')
    desc = request.form.get('descripcion')
    nueva_excepcion = ExcepcionHorario(
        fecha=datetime.strptime(fecha_str, '%Y-%m-%d').date(),
        descripcion=desc,
        es_cerrado=True
    )
    db.session.add(nueva_excepcion)
    db.session.commit()
    return redirect(url_for('admin.index', tab='horarios'))



@admin_bp.route('/eliminar_festivo/<int:id>')
@login_required
def eliminar_festivo(id):
    if not current_user.es_admin:
        return redirect(url_for('index'))
    
    festivo = ExcepcionHorario.query.get_or_404(id)
    db.session.delete(festivo)
    db.session.commit()
    flash("Día festivo eliminado. El calendario vuelve a la normalidad.")
    return redirect(url_for('admin.index', tab='horarios'))