from flask import Blueprint, request, redirect, url_for, flash, jsonify
from flask_login import current_user
from database.models import db, Cita, Peluquero, Servicio
from datetime import datetime, timedelta

citas_bp = Blueprint('citas', __name__)

@citas_bp.route('/reservar', methods=['POST'])
def reservar():
    print("\n--- INICIO DE RESERVA INTELIGENTE ---")
    
    # 1. Identificar al usuario
    if current_user.is_authenticated:
        nombre = current_user.nombre
        telefono = current_user.telefono
        usuario_id = current_user.id
    else:
        nombre = request.form.get('nombre')
        telefono = request.form.get('telefono')
        usuario_id = None

    # 2. Capturar datos del formulario
    fecha_str = request.form.get('fecha')
    hora_str = request.form.get('hora')
    servicio = request.form.get('servicio')

    try:
        # Conversión de formatos
        fecha_obj = datetime.strptime(fecha_str, '%Y-%m-%d').date()
        try:
            hora_obj = datetime.strptime(hora_str, '%H:%M').time()
        except ValueError:
            hora_obj = datetime.strptime(hora_str, '%H:%M:%S').time()

        # 3. Lógica de asignación de Peluquero
        # ¿Qué día de la semana es? (0=Lunes, 1=Martes... 5=Sábado, 6=Domingo)
        dia_semana_index = str(fecha_obj.weekday()) 

        # Buscamos peluqueros que trabajen ese día de la semana
        peluqueros_que_curran = Peluquero.query.filter(
            Peluquero.activo == True,
            Peluquero.dias_laborables.contains(dia_semana_index)
        ).all()

        peluquero_asignado_id = None

        for p in peluqueros_que_curran:
            # Comprobar si la hora elegida está dentro de SU horario de mañana o tarde
            # Convertimos las horas de la DB (string) a objeto time para comparar
            h_inicio_m = datetime.strptime(p.h_inicio_manana, '%H:%M').time()
            h_fin_m = datetime.strptime(p.h_fin_manana, '%H:%M').time()
            h_inicio_t = datetime.strptime(p.h_inicio_tarde, '%H:%M').time()
            h_fin_t = datetime.strptime(p.h_fin_tarde, '%H:%M').time()

            esta_en_horario = (h_inicio_m <= hora_obj < h_fin_m) or (h_inicio_t <= hora_obj < h_fin_t)

            if esta_en_horario:
                # Si está en su horario, ver si ya tiene una cita a esa misma hora
                cita_existente = Cita.query.filter_by(
                    fecha=fecha_obj, 
                    hora=hora_obj, 
                    peluquero_id=p.id
                ).first()

                if not cita_existente:
                    # ¡Bingo! Este peluquero trabaja y está libre
                    peluquero_asignado_id = p.id
                    break # Dejamos de buscar, ya tenemos uno

        # 4. Finalizar reserva
        if peluquero_asignado_id:
            nueva_cita = Cita(
                fecha=fecha_obj,
                hora=hora_obj,
                peluquero_id=peluquero_asignado_id,
                servicio=servicio,
                usuario_id=usuario_id,
                nombre_invitado=nombre if not usuario_id else None,
                telefono_cliente=telefono
            )
            db.session.add(nueva_cita)
            db.session.commit()
            
            print(f"✅ RESERVA OK: Asignada a Peluquero ID {peluquero_asignado_id}")
            flash(f"¡Cita confirmada para el {fecha_str} a las {hora_str}!")
            return redirect(url_for('contacto'))
        else:
            print("❌ ERROR: No hay peluqueros disponibles en ese horario.")
            flash("Lo sentimos, no hay hueco disponible a esa hora o el centro está cerrado.")
            return redirect(url_for('contacto'))

    except Exception as e:
        db.session.rollback()
        print(f"❌ ERROR CRÍTICO: {str(e)}")
        flash(f"Error al procesar la reserva: {e}")
        return redirect(url_for('contacto'))



def generar_franjas(inicio_str, fin_str):
    """Genera lista de horas cada 30 min entre dos strings 'HH:MM'"""
    franjas = []
    fmt = '%H:%M'
    try:
        actual = datetime.strptime(inicio_str, fmt)
        fin = datetime.strptime(fin_str, fmt)
        while actual < fin:
            franjas.append(actual.strftime(fmt))
            actual += timedelta(minutes=30)
    except:
        pass
    return franjas

@citas_bp.route('/api/disponibilidad')
def check_disponibilidad():
    fecha_str = request.args.get('fecha')
    if not fecha_str:
        return jsonify([])

    try:
        dia_semana = str(datetime.strptime(fecha_str, '%Y-%m-%d').weekday())
        peluqueros = Peluquero.query.filter_by(activo=True).all()
        horas_libres = set()

        for p in peluqueros:
            # 1. ¿Trabaja este peluquero este día de la semana?
            if dia_semana in p.dias_laborables.split(','):
                
                # 2. Generamos franjas REALES de su horario de mañana y tarde
                franjas_manana = generar_franjas(p.h_inicio_manana, p.h_fin_manana)
                franjas_tarde = generar_franjas(p.h_inicio_tarde, p.h_fin_tarde)
                todas_sus_franjas = franjas_manana + franjas_tarde
                
                # 3. Miramos qué tiene ya ocupado
                fecha_obj = datetime.strptime(fecha_str, '%Y-%m-%d').date()
                citas_hoy = Cita.query.filter_by(fecha=fecha_obj, peluquero_id=p.id).all()
                horas_cogidas = [c.hora.strftime('%H:%M') for c in citas_hoy]
                
                # 4. Solo añadimos las horas que están en su horario Y no están cogidas
                for f in todas_sus_franjas:
                    if f not in horas_cogidas:
                        horas_libres.add(f)

        # Devolvemos la lista limpia y ordenada
        return jsonify(sorted(list(horas_libres)))
    except Exception as e:
        print(f"Error en API: {e}")
        return jsonify([]), 500