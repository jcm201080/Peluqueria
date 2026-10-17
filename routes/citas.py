import os
import json
from flask import Blueprint, request, redirect, url_for, flash, jsonify, render_template, current_app
from flask_login import current_user
from database.models import db, Cita, Peluquero, Servicio, HorarioPeluquero, ExcepcionHorario
from datetime import datetime, timedelta

citas_bp = Blueprint('citas', __name__)

DIAS_ES = ["Lunes", "Martes", "Miércoles", "Jueves", "Viernes", "Sábado", "Domingo"]
MESES_ES = ["Ene", "Feb", "Mar", "Abr", "May", "Jun", "Jul", "Ago", "Sep", "Oct", "Nov", "Dic"]

# ==========================================
# 🛠️ NÚCLEO DE ASIGNACIÓN Y PRIORIDAD
# ==========================================

def leer_config_prioridad():
    """Lee el estado del interruptor de prioridades desde el JSON"""
    try:
        ruta_json = os.path.join(current_app.root_path, 'config_web.json')
        with open(ruta_json, 'r', encoding='utf-8') as f:
            config = json.load(f)
            return config.get("usar_prioridades", False)
    except Exception:
        return False

def obtener_disponibilidad_del_dia(fecha_obj):
    """
    Motor híbrido: 
    Si usar_prioridades=False, une todos los huecos por igual.
    Si usar_prioridades=True, llena los peluqueros de prioridad 1 antes de mostrar los del 2.
    Devuelve siempre una lista agrupada: [{'hora': '10:00', 'peluqueros': [{'id': 1, 'nombre': 'Juan'}]}]
    """
    try:
        peluqueros = Peluquero.query.filter_by(activo=True).order_by(Peluquero.prioridad.asc()).all()
    except Exception:
        peluqueros = Peluquero.query.filter_by(activo=True).order_by(Peluquero.id.asc()).all()

    if not peluqueros:
        return []

    usar_prioridades = leer_config_prioridad()

    # --- MODO 1: SIN PRIORIDADES (Reparto equitativo) ---
    if not usar_prioridades:
        huecos_agrupados = {}
        for p in peluqueros:
            horario = obtener_horario_activo_peluquero(p.id, fecha_obj)
            if not horario: continue

            franjas = generar_franjas(horario.get('h_im'), horario.get('h_fm')) + \
                      generar_franjas(horario.get('h_it'), horario.get('h_ft'))
            
            citas_hoy = Cita.query.filter_by(fecha=fecha_obj, peluquero_id=p.id).all()
            horas_cogidas = {c.hora.strftime('%H:%M') for c in citas_hoy}

            for h in franjas:
                if h not in horas_cogidas:
                    if h not in huecos_agrupados:
                        huecos_agrupados[h] = []
                    huecos_agrupados[h].append({'id': p.id, 'nombre': p.nombre})
        
        return [{'hora': h, 'peluqueros': huecos_agrupados[h]} for h in sorted(huecos_agrupados.keys())]

    # --- MODO 2: CON PRIORIDADES (Se llena nivel a nivel) ---
    niveles_prioridad = sorted(list(set(getattr(p, 'prioridad', 1) for p in peluqueros)))

    for nivel in niveles_prioridad:
        peluqueros_en_nivel = [p for p in peluqueros if getattr(p, 'prioridad', 1) == nivel]
        huecos_agrupados = {}

        for p in peluqueros_en_nivel:
            horario = obtener_horario_activo_peluquero(p.id, fecha_obj)
            if not horario: continue

            franjas = generar_franjas(horario.get('h_im'), horario.get('h_fm')) + \
                      generar_franjas(horario.get('h_it'), horario.get('h_ft'))
            
            citas_hoy = Cita.query.filter_by(fecha=fecha_obj, peluquero_id=p.id).all()
            horas_cogidas = {c.hora.strftime('%H:%M') for c in citas_hoy}

            for h in franjas:
                if h not in horas_cogidas:
                    if h not in huecos_agrupados:
                        huecos_agrupados[h] = []
                    huecos_agrupados[h].append({'id': p.id, 'nombre': p.nombre})
        
        # Si hemos encontrado huecos en este nivel de prioridad, cortamos y enviamos solo estos.
        if huecos_agrupados:
            return [{'hora': h, 'peluqueros': huecos_agrupados[h]} for h in sorted(huecos_agrupados.keys())]
            
    return []

def obtener_horas_libres_por_fecha(fecha_obj):
    # Puente optimizado para el calendario
    dispo = obtener_disponibilidad_del_dia(fecha_obj)
    return set([hueco['hora'] for hueco in dispo])

def obtener_calendario_separado(num_dias=15):
    hoy = datetime.now().date()
    limite_habitual = hoy + timedelta(days=num_dias)
    dias_normales = []
    dias_especiales = []

    for i in range(30):
        fecha = hoy + timedelta(days=i)
        if fecha.weekday() == 6: continue
        if obtener_horas_libres_por_fecha(fecha):
            dias_normales.append({
                'valor': fecha.strftime('%Y-%m-%d'),
                'texto': f"{DIAS_ES[fecha.weekday()]}, {fecha.day} {MESES_ES[fecha.month - 1]}"
            })
        if len(dias_normales) == 15: break

    if not dias_normales:
        return {'normales': [], 'especiales': []}
        
    fecha_limite = datetime.strptime(dias_normales[-1]['valor'], '%Y-%m-%d').date()
    especiales_db = ExcepcionHorario.query.filter(
        ExcepcionHorario.fecha > fecha_limite,
        ExcepcionHorario.es_cerrado == False
    ).order_by(ExcepcionHorario.fecha.asc()).all()

    for esp in especiales_db:
        if obtener_horas_libres_por_fecha(esp.fecha):
            dias_especiales.append({
                'valor': esp.fecha.strftime('%Y-%m-%d'),
                'texto': f"{DIAS_ES[esp.fecha.weekday()]}, {esp.fecha.day} {MESES_ES[esp.fecha.month - 1]}"
            })
    return {'normales': dias_normales, 'especiales': dias_especiales}

@citas_bp.route('/contacto')
def contacto():
    servicios = Servicio.query.all()
    hoy = datetime.now().date()
    
    proximas_citas = []
    if current_user.is_authenticated:
        proximas_citas = Cita.query.filter(
            Cita.usuario_id == current_user.id,
            Cita.fecha >= hoy
        ).order_by(Cita.fecha.asc(), Cita.hora.asc()).limit(3).all()

    calendario = obtener_calendario_separado()
    
    return render_template('contacto.html', 
                           servicios=servicios, 
                           dias=calendario['normales'], 
                           especiales=calendario['especiales'],
                           proximas_citas=proximas_citas)

# --- Funciones de apoyo menores ---

def generar_franjas(inicio_str, fin_str):
    franjas = []
    if not inicio_str or not fin_str: return franjas
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
    dia_semana_int = fecha_obj.weekday()
    if ExcepcionHorario.query.filter_by(fecha=fecha_obj, es_cerrado=True, peluquero_id=None).first():
        return None
    excep_propia = ExcepcionHorario.query.filter_by(fecha=fecha_obj, peluquero_id=p_id).first()
    if excep_propia:
        if excep_propia.es_cerrado: return None
        return {'h_im': excep_propia.h_inicio_m, 'h_fm': excep_propia.h_fin_m,
                'h_it': excep_propia.h_inicio_t, 'h_ft': excep_propia.h_fin_t}
    excep_general = ExcepcionHorario.query.filter_by(fecha=fecha_obj, es_cerrado=False, peluquero_id=None).first()
    if excep_general:
        return {'h_im': excep_general.h_inicio_m, 'h_fm': excep_general.h_fin_m,
                'h_it': excep_general.h_inicio_t, 'h_ft': excep_general.h_fin_t}
    h_normal = HorarioPeluquero.query.filter_by(peluquero_id=p_id, dia_semana=dia_semana_int).first()
    if h_normal and h_normal.trabaja:
        return {'h_im': h_normal.h_inicio_m, 'h_fm': h_normal.h_fin_m,
                'h_it': h_normal.h_inicio_t, 'h_ft': h_normal.h_fin_t}
    return None

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
        # El motor devuelve la lista lista y agrupada para pintar en JS
        resultados = obtener_disponibilidad_del_dia(fecha_obj)
        return jsonify(resultados)
    except Exception as e:
        print(f"❌ Error en API Disponibilidad: {e}")
        return jsonify([]), 500

@citas_bp.route('/api/disponibilidad-mensual')
def disponibilidad_mensual():
    try:
        dias_ocupados = []
        for i in range(30):
            fecha_obj = datetime.now().date() + timedelta(days=i)
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
            # Motor centralizado que soporta ambos modos (con y sin prioridades)
            dispo = obtener_disponibilidad_del_dia(fecha_obj)
            opciones_libres = []
            
            for hueco in dispo:
                if hueco['hora'] == hora_str_simple:
                    opciones_libres = [p['id'] for p in hueco['peluqueros']]
                    break
            
            if opciones_libres:
                peluquero_asignado_id = opciones_libres[0]

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
                return redirect(url_for('citas.contacto'))

        else:
            flash("Lo sentimos, otro cliente acaba de reservar este hueco o el profesional no está disponible.", "error")
            return redirect(url_for('citas.contacto'))

    except Exception as e:
        db.session.rollback()
        flash(f"Error al procesar la reserva: {e}", "error")
        return redirect(url_for('citas.contacto'))

# ==========================================
# 👤 RUTAS DE CLIENTES Y GESTIÓN DE CITAS
# ==========================================

@citas_bp.route('/buscar-cita', methods=['POST'])
def buscar_cita():
    telefono = request.form.get('telefono_buscar', '').strip()
    servicios = Servicio.query.all()
    calendario = obtener_calendario_separado()

    if not telefono:
        flash("Por favor, introduce un número de teléfono.", "error")
        return redirect(url_for('citas.contacto'))

    citas_encontradas = Cita.query.filter_by(telefono_cliente=telefono).order_by(Cita.fecha.desc()).all()
    
    return render_template('contacto.html', 
                           citas_buscadas=citas_encontradas, 
                           telefono_buscado=telefono,
                           busqueda_realizada=True,
                           servicios=servicios,
                           dias=calendario['normales'],
                           especiales=calendario['especiales'])

@citas_bp.route('/eliminar-cliente/<int:id>', methods=['POST'])
def eliminar_cita_cliente(id):
    cita = Cita.query.get_or_404(id)
    db.session.delete(cita)
    db.session.commit()
    flash("Tu cita ha sido anulada correctamente.", "success")
    return redirect(url_for('citas.contacto'))

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
        return redirect(url_for('citas.contacto'))
        
    servicios = Servicio.query.all()
    calendario = obtener_calendario_separado()
        
    return render_template('modificar_cita.html', 
                           cita=cita, 
                           servicios=servicios, 
                           dias=calendario['normales'],
                           especiales=calendario['especiales'])