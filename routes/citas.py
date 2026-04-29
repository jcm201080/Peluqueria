from flask import Blueprint, request, redirect, url_for, flash, jsonify
from flask_login import current_user
from database.models import db, Cita, Peluquero, Servicio, HorarioPeluquero, ExcepcionHorario
from datetime import datetime, timedelta
import urllib.parse


citas_bp = Blueprint('citas', __name__)

def generar_franjas(inicio_str, fin_str):
    """Genera lista de horas cada 30 min entre dos strings 'HH:MM'"""
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

@citas_bp.route('/api/disponibilidad')
def check_disponibilidad():
    fecha_str = request.args.get('fecha')
    if not fecha_str:
        return jsonify([])

    try:
        fecha_obj = datetime.strptime(fecha_str, '%Y-%m-%d').date()
        dia_semana_int = fecha_obj.weekday()

        # 1. Verificar si hay un cierre total (festivo para todos)
        cierre_total = ExcepcionHorario.query.filter_by(fecha=fecha_obj, es_cerrado=True, peluquero_id=None).first()
        if cierre_total:
            return jsonify([]) 

        peluqueros = Peluquero.query.filter_by(activo=True).all()
        horas_libres = set()

        for p in peluqueros:
            # --- NUEVA LÓGICA DE PRIORIDAD ---
            
            # 2. ¿Tiene este peluquero una excepción (horario especial o cierre individual) para hoy?
            excep = ExcepcionHorario.query.filter_by(fecha=fecha_obj, peluquero_id=p.id).first()
            
            horario_a_usar = None
            
            if excep:
                if not excep.es_cerrado:
                    # Es un horario especial: creamos un objeto temporal con las horas de la excepción
                    horario_a_usar = {
                        'h_im': excep.h_inicio_m, 'h_fm': excep.h_fin_m,
                        'h_it': excep.h_inicio_t, 'h_ft': excep.h_fin_t
                    }
                else:
                    # El peluquero está de vacaciones o libre hoy, saltamos al siguiente peluquero
                    continue
            else:
                # 3. Si no hay excepción, buscamos su horario normal de la semana
                h_normal = HorarioPeluquero.query.filter_by(peluquero_id=p.id, dia_semana=dia_semana_int).first()
                if h_normal and h_normal.trabaja:
                    horario_a_usar = {
                        'h_im': h_normal.h_inicio_m, 'h_fm': h_normal.h_fin_m,
                        'h_it': h_normal.h_inicio_t, 'h_ft': h_normal.h_fin_t
                    }

            # 4. Si tenemos un horario definido (normal o especial), generamos las franjas
            if horario_a_usar:
                franjas_m = generar_franjas(horario_a_usar['h_im'], horario_a_usar['h_fm'])
                franjas_t = generar_franjas(horario_a_usar['h_it'], horario_a_usar['h_ft'])
                todas_sus_franjas = franjas_m + franjas_t
                
                # 5. Filtrar las ya ocupadas
                citas_hoy = Cita.query.filter_by(fecha=fecha_obj, peluquero_id=p.id).all()
                horas_cogidas = [c.hora.strftime('%H:%M') for c in citas_hoy]
                
                for f in todas_sus_franjas:
                    if f not in horas_cogidas:
                        horas_libres.add(f)

        return jsonify(sorted(list(horas_libres)))

    except Exception as e:
        print(f"❌ Error en API Disponibilidad: {e}")
        return jsonify([]), 500

@citas_bp.route('/reservar', methods=['POST'])
def reservar():
    fecha_str = request.form.get('fecha')
    hora_str = request.form.get('hora')
    servicio = request.form.get('servicio')
    peluquero_id_manual = request.form.get('peluquero_id') 

    # Lógica de identificación de usuario (se mantiene intacta)
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

    # Usamos un solo bloque try-except general para cazar cualquier error
    try:
        fecha_obj = datetime.strptime(fecha_str, '%Y-%m-%d').date()
        hora_obj = datetime.strptime(hora_str[:5], '%H:%M').time()
        dia_semana_int = fecha_obj.weekday()

        peluquero_asignado_id = None

        # Si el admin elige uno, verificamos disponibilidad rápida
        if peluquero_id_manual:
            peluquero_asignado_id = int(peluquero_id_manual)
        else:
            # Búsqueda automática de peluquero disponible
            peluqueros = Peluquero.query.filter_by(activo=True).all()
            for p in peluqueros:
                horario_dia = HorarioPeluquero.query.filter_by(
                    peluquero_id=p.id, 
                    dia_semana=dia_semana_int
                ).first()

                if horario_dia and horario_dia.trabaja:
                    # Comprobar si la hora cae en sus turnos
                    h_im = datetime.strptime(horario_dia.h_inicio_m, '%H:%M').time()
                    h_fm = datetime.strptime(horario_dia.h_fin_m, '%H:%M').time()
                    h_it = datetime.strptime(horario_dia.h_inicio_t, '%H:%M').time()
                    h_ft = datetime.strptime(horario_dia.h_fin_t, '%H:%M').time()

                    esta_en_horario = (h_im <= hora_obj < h_fm) or (h_it <= hora_obj < h_ft)
                    
                    if esta_en_horario:
                        ocupada = Cita.query.filter_by(fecha=fecha_obj, hora=hora_obj, peluquero_id=p.id).first()
                        if not ocupada:
                            peluquero_asignado_id = p.id
                            break

        # Si encontramos un peluquero disponible
        if peluquero_asignado_id:
            nueva_cita = Cita(
                fecha=fecha_obj,
                hora=hora_obj,
                peluquero_id=peluquero_asignado_id,
                servicio=servicio if servicio else "Reserva Manual",
                usuario_id=usuario_id,
                nombre_invitado=nombre if not usuario_id else None,
                telefono_cliente=telefono
            )
            db.session.add(nueva_cita)
            db.session.commit()
            
            # --- REDIRECCIÓN TRAS GUARDAR LA CITA ---
            if current_user.is_authenticated and current_user.es_admin:
                # Si es el ADMIN quien reserva desde su panel
                flash(f"✅ Cita confirmada para {nombre}", "success")
                return redirect(url_for('admin.gestion_diaria', fecha_busqueda=fecha_str))
            else:
                # --- AQUÍ LA MEJORA PARA CLIENTES E INVITADOS ---
                # Formateamos la fecha para que sea más legible (dd/mm/aaaa)
                # En citas.py, dentro de reservar():

                fecha_bonita = fecha_obj.strftime('%d/%m/%Y')

                mensaje_confirmacion = (
                    f"<strong>✅ ¡Cita confirmada para {nombre}!</strong><br>"
                    f"📞 <b>Teléfono:</b> {telefono}<br>"
                    f"📅 <b>Día:</b> {fecha_bonita} a las 🕒 {hora_str}h.<br><br>"
                    f"⚠️ <i>Si no puede venir, por favor avise con antelación.</i>"
                )

                flash(mensaje_confirmacion, "success") # "success" suele poner el fondo verde en CSS
                
                return redirect(url_for('contacto'))

        else:
            # Si el bucle termina y peluquero_asignado_id sigue siendo None
            flash("Lo sentimos, no hay hueco disponible con ese profesional en este horario.", "error")
            return redirect(url_for('contacto'))

    except Exception as e:
        # Si algo falla en la base de datos o al transformar la fecha
        db.session.rollback()
        flash(f"Error al reservar: {e}", "error")
        return redirect(url_for('contacto'))