from flask import Blueprint, request, redirect, url_for, flash
from flask_login import current_user
from database.models import db, Cita, Peluquero, Servicio
from datetime import datetime

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