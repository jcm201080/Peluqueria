from flask import Blueprint, render_template, redirect, url_for, request, flash
from flask_login import login_required, current_user
from database.models import db, Cita, Peluquero, Servicio, Configuracion

admin_bp = Blueprint('admin', __name__, url_prefix='/admin')

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