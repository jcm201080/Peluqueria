from flask import Blueprint, request, redirect, url_for, flash, jsonify, render_template
from flask_login import current_user
from database.models import db, Cita, Peluquero, Servicio, HorarioPeluquero, ExcepcionHorario
from datetime import datetime, timedelta

citas_bp = Blueprint('citas', __name__)

# ==========================================
# 🛠️ FUNCIONES DE APOYO (HELPERS)
# ==========================================

# Mapeo estático para garantizar el español sin depender del servidor (VPS)
DIAS_ES = ["Lunes", "Martes", "Miércoles", "Jueves", "Viernes", "Sábado", "Domingo"]
MESES_ES = ["Ene", "Feb", "Mar", "Abr", "May", "Jun", "Jul", "Ago", "Sep", "Oct", "Nov", "Dic"]

def obtener_dias_proximos(num_dias=15):
    """Genera la lista de días para el selector en el frontend en español garantizado."""
    dias = []
    for i in range(num_dias):
        fecha = datetime.now() + timedelta(days=i)
        
        # Extraemos los índices (weekday: 0=Lunes, 6=Domingo | month: 1=Enero, 12=Diciembre)
        nombre_dia = DIAS_ES[fecha.weekday()]
        nombre_mes = MESES_ES[fecha.month - 1]
        
        dias.append({
            'valor': fecha.strftime('%Y-%m-%d'),
            'texto': f"{nombre_dia}, {fecha.day} {nombre_mes}"
        })
    return dias

def generar_franjas(inicio_str, fin_str):
    """Genera lista de horas cada 30 min entre dos strings 'HH:MM'."""
    franjas = []
    if not inicio_str or not fin_str:
        return franjas
    fmt = '%H:%M'
    try:
        actual = datetime.strptime(inicio_str, fmt)
        fin = datetime.strptime(fin_str, fmt)
        while actual < fin:
            franjas.append(actual.strftime(fmt))
            actual += timedelta(minutes=30)
    except Exception as e:
        print(f"Error generando franjas: {e}")
    return franjas

def obtener_horario_activo_peluquero(p_id, fecha_obj):
    """
    NÚCLEO DEL SISTEMA: Determina el horario real de un peluquero para un día específico.
    Prioridad: 1. Cierre total -> 2. Excepción propia -> 3. Excepción general -> 4. Horario normal.
    Retorna un diccionario con las horas o None si no trabaja.
    """
    dia_semana_int = fecha_obj.weekday()

    # 1. Cierre total (Festivo general)
    if ExcepcionHorario.query.filter_by(fecha=fecha_obj, es_cerrado=True, peluquero_id=None).first():
        return None

    # 2. Excepción propia del peluquero
    excep_propia = ExcepcionHorario.query.filter_by(fecha=fecha_obj, peluquero_id=p_id).first()
    if excep_propia:
        if excep_propia.es_cerrado:
            return None
        return {
            'h_im': excep_propia.h_inicio_m, 'h_fm': excep_propia.h_fin_m,
            'h_it': excep_propia.h_inicio_t, 'h_ft': excep_propia.h_fin_t
        }

    # 3. Excepción general (Horario especial para toda la peluquería)
    excep_general = ExcepcionHorario.query.filter_by(fecha=fecha_obj, es_cerrado=False, peluquero_id=None).first()
    if excep_general:
        return {
            'h_im': excep_general.h_inicio_m, 'h_fm': excep_general.h_fin_m,
            'h_it': excep_general.h_inicio_t, 'h_ft': excep_general.h_fin_t
        }

    # 4. Horario normal
    h_normal = HorarioPeluquero.query.filter_by(peluquero_id=p_id, dia_semana=dia_semana_int).first()
    if h_normal and h_normal.trabaja:
        return {
            'h_im': h_normal.h_inicio_m, 'h_fm': h_normal.h_fin_m,
            'h_it': h_normal.h_inicio_t, 'h_ft': h_normal.h_fin_t
        }

    return None

def obtener_horas_libres_por_fecha(fecha_obj):
    """Devuelve un set con las horas libres para la fecha dada."""
    peluqueros = Peluquero.query.filter_by(activo=True).all()
    horas_libres = set()

    for p in peluqueros:
        horario_a_usar = obtener_horario_activo_peluquero(p.id, fecha_obj)
        
        if horario_a_usar:
            # Generamos todos sus huecos del día
            franjas = generar_franjas(horario_a_usar.get('h_im'), horario_a_usar.get('h_fm')) + \
                      generar_franjas(horario_a_usar.get('h_it'), horario_a_usar.get('h_ft'))
            
            # Consultamos las citas que ya tiene cogidas hoy
            citas_hoy = Cita.query.filter_by(fecha=fecha_obj, peluquero_id=p.id).all()
            horas_cogidas = [c.hora.strftime('%H:%M') for c in citas_hoy]
            
            # Si el hueco no está cogido, lo añadimos a la lista de horas libres globales
            for f in franjas:
                if f not in horas_cogidas:
                    horas_libres.add(f)

    return horas_libres


# ==========================================
# 🌐 RUTAS DE LA API (FRONTEND)
# ==========================================

@citas_bp.route('/api/disponibilidad')
def check_disponibilidad():
    fecha_str = request.args.get('fecha')
    if not fecha_str:
        return jsonify([])

    try:
        fecha_obj = datetime.strptime(fecha_str, '%Y-%m-%d').date()
        horas_libres = obtener_horas_libres_por_fecha(fecha_obj)
        return jsonify(sorted(list(horas_libres)))
    except Exception as e:
        print(f"❌ Error en API Disponibilidad: {e}")
        return jsonify([]), 500

@citas_bp.route('/api/disponibilidad-mensual')
def disponibilidad_mensual():
    try:
        dias_ocupados = []
        for i in range(30):
            fecha_obj = datetime.now().date() + timedelta(days=i)
            # Descartar domingos directamente
            if fecha_obj.weekday() == 6:
                dias_ocupados.append(fecha_obj.strftime('%Y-%m-%d'))
                continue
                
            horas_libres = obtener_horas_libres_por_fecha(fecha_obj)
            if not horas_libres:
                dias_ocupados.append(fecha_obj.strftime('%Y-%m-%d'))
                
        return jsonify({"dias_ocupados": dias_ocupados})
    except Exception as e:
        print(f"❌ Error en API Disponibilidad Mensual: {e}")
        return jsonify({"dias_ocupados": []}), 500

@citas_bp.route('/api/dias-ocupados')
def dias_ocupados():
    cierres = ExcepcionHorario.query.filter_by(es_cerrado=True, peluquero_id=None).all()
    fechas_bloqueadas = [c.fecha.strftime('%Y-%m-%d') for c in cierres]
    return jsonify(fechas_bloqueadas)


# ==========================================
# 💾 RUTAS DE ACCIÓN (BACKEND)
# ==========================================

@citas_bp.route('/reservar', methods=['POST'])
def reservar():
    fecha_str = request.form.get('fecha')
    hora_str = request.form.get('hora')
    servicio = request.form.get('servicio')
    peluquero_id_manual = request.form.get('peluquero_id') 

    # 1. Gestión de la Identidad del usuario
    if current_user.is_authenticated and current_user.es_admin and request.form.get('nombre'):
        nombre = f"Admin: {request.form.get('nombre')}"
        telefono = request.form.get('telefono', 'S/N')
        usuario_id = None
    elif current_user.is_authenticated:
        nombre = current_user.nombre
        telefono = current_user.telefono
        usuario_id = current_user.id
    else:
        nombre = request.form.get('nombre')
        telefono = request.form.get('telefono')
        usuario_id = None

    try:
        fecha_obj = datetime.strptime(fecha_str, '%Y-%m-%d').date()
        hora_obj = datetime.strptime(hora_str[:5], '%H:%M').time()
        hora_str_simple = hora_obj.strftime('%H:%M')

        peluquero_asignado_id = None

        if peluquero_id_manual:
            peluquero_asignado_id = int(peluquero_id_manual)
        else:
            # 2. Motor de Asignación Automática (¡Ahora sincronizado con la API!)
            peluqueros = Peluquero.query.filter_by(activo=True).all()
            for p in peluqueros:
                horario_a_usar = obtener_horario_activo_peluquero(p.id, fecha_obj)
                
                if horario_a_usar:
                    # Generamos los huecos exactos válidos para este peluquero hoy
                    franjas_validas = generar_franjas(horario_a_usar.get('h_im'), horario_a_usar.get('h_fm')) + \
                                      generar_franjas(horario_a_usar.get('h_it'), horario_a_usar.get('h_ft'))
                    
                    # Si la hora que pide el cliente es una franja válida para el peluquero
                    if hora_str_simple in franjas_validas:
                        ocupada = Cita.query.filter_by(fecha=fecha_obj, hora=hora_obj, peluquero_id=p.id).first()
                        if not ocupada:
                            peluquero_asignado_id = p.id
                            break # Encontramos peluquero, rompemos el bucle

        # 3. Guardado en Base de Datos
        if peluquero_asignado_id:
            nueva_cita = Cita(
                fecha=fecha_obj, hora=hora_obj,
                peluquero_id=peluquero_asignado_id,
                servicio=servicio if servicio else "Reserva Manual",
                usuario_id=usuario_id,
                nombre_invitado=nombre if not usuario_id else None,
                telefono_cliente=telefono
            )
            db.session.add(nueva_cita)
            db.session.commit()
            
            if current_user.is_authenticated and current_user.es_admin:
                flash(f"✅ Cita confirmada para {nombre}", "success")
                return redirect(url_for('admin.gestion_diaria', fecha_busqueda=fecha_str))
            else:
                fecha_bonita = fecha_obj.strftime('%d/%m/%Y')
                mensaje_confirmacion = (
                    f"<strong>✅ ¡Cita confirmada para {nombre}!</strong><br>"
                    f"📞 <b>Teléfono:</b> {telefono}<br>"
                    f"📅 <b>Día:</b> {fecha_bonita} a las 🕒 {hora_str_simple}h.<br><br>"
                    f"⚠️ <i>Si no puedes venir, por favor avísanos con antelación.</i>"
                )
                flash(mensaje_confirmacion, "success")
                return redirect(url_for('contacto'))

        else:
            flash("Lo sentimos, otro cliente acaba de reservar este hueco o el peluquero no está disponible.", "error")
            return redirect(url_for('contacto'))

    except Exception as e:
        db.session.rollback()
        flash(f"Error al procesar la reserva: {e}", "error")
        return redirect(url_for('contacto'))


# ==========================================
# 👤 RUTAS DE CLIENTES Y GESTIÓN DE CITAS
# ==========================================

@citas_bp.route('/buscar-cita', methods=['POST'])
def buscar_cita():
    telefono = request.form.get('telefono_buscar', '').strip()
    servicios = Servicio.query.all()
    dias = obtener_dias_proximos()

    if not telefono:
        flash("Por favor, introduce un número de teléfono.", "error")
        return redirect(url_for('contacto'))

    citas_encontradas = Cita.query.filter_by(telefono_cliente=telefono).order_by(Cita.fecha.desc()).all()
    
    return render_template('contacto.html', 
                           citas_buscadas=citas_encontradas, 
                           telefono_buscado=telefono,
                           busqueda_realizada=True,
                           servicios=servicios,
                           dias=dias)

@citas_bp.route('/eliminar-cliente/<int:id>', methods=['POST'])
def eliminar_cita_cliente(id):
    cita = Cita.query.get_or_404(id)
    db.session.delete(cita)
    db.session.commit()
    flash("Tu cita ha sido anulada correctamente.", "success")
    return redirect(url_for('contacto'))

@citas_bp.route('/modificar/<int:id>', methods=['GET', 'POST'])
def modificar_cita(id):
    cita = Cita.query.get_or_404(id)
    
    if request.method == 'POST':
        nuevo_servicio = request.form.get('servicio')
        nueva_fecha = request.form.get('fecha')
        nueva_hora = request.form.get('hora')
        
        cita.servicio = nuevo_servicio
        cita.fecha = datetime.strptime(nueva_fecha, '%Y-%m-%d').date()
        cita.hora = datetime.strptime(nueva_hora, '%H:%M').time()
        
        db.session.commit()
        
        fecha_str = cita.fecha.strftime('%d/%m/%Y')
        hora_str = cita.hora.strftime('%H:%M')
        
        flash(f"✅ La cita ha sido modificada al día {fecha_str} a las {hora_str}.", "success")
        return redirect(url_for('contacto'))
        
    servicios = Servicio.query.all()
    dias_disponibles = obtener_dias_proximos()
        
    return render_template('modificar_cita.html', cita=cita, servicios=servicios, dias=dias_disponibles)