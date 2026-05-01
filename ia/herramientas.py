# ia/herramientas.py
import json
from datetime import datetime
from database.models import db, Cita, Peluquero # Importamos tus modelos reales[cite: 2]

# ia/herramientas.py (Actualización de la función)

def consultar_disponibilidad_db(fecha):
    """Devuelve una lista unificada de horas libres, sin importar el peluquero."""
    try:
        fecha_obj = datetime.strptime(fecha, "%Y-%m-%d").date()
        
        # 1. Definimos las horas de trabajo estándar (Puedes ajustar esto a tu horario real)
        horas_posibles = [
            "09:00", "09:30", "10:00", "10:30", "11:00", "11:30", "12:00", "12:30", "13:00", "13:30",
            "16:00", "16:30", "17:00", "17:30", "18:00", "18:30", "19:00", "19:30", "20:00"
        ]
        
        # 2. Vemos cuántos peluqueros trabajan en total
        total_peluqueros = Peluquero.query.filter_by(activo=True).count()
        if total_peluqueros == 0:
            return "Actualmente no hay peluqueros activos en el sistema."

        # 3. Buscamos todas las citas de ese día
        citas_del_dia = Cita.query.filter_by(fecha=fecha_obj).all()
        
        # 4. Contamos cuántas citas hay en cada hora
        ocupacion_por_hora = {}
        for c in citas_del_dia:
            h_str = c.hora.strftime("%H:%M")
            ocupacion_por_hora[h_str] = ocupacion_por_hora.get(h_str, 0) + 1
            
        # 5. Filtramos solo las horas donde NO están todos los peluqueros ocupados
        horas_libres = []
        for h in horas_posibles:
            # Si hay menos citas a esa hora que peluqueros totales, hay hueco
            if ocupacion_por_hora.get(h, 0) < total_peluqueros:
                horas_libres.append(h)
                
        if not horas_libres:
            return f"Lo siento, tenemos la agenda totalmente llena para el día {fecha}."
            
        return f"Tenemos hueco a estas horas el {fecha}: {', '.join(horas_libres)}. Pregúntale al cliente a qué hora le viene bien y pídele su nombre y teléfono para reservar."
        
    except Exception as e:
        return f"Error al consultar la disponibilidad: {e}"

def consultar_mis_citas_db(telefono):
    """Busca las citas de un cliente por su teléfono."""
    try:
        hoy = datetime.now().date()
        # Buscamos citas de ese teléfono que sean de hoy en adelante
        citas = Cita.query.filter(Cita.telefono_cliente == telefono, Cita.fecha >= hoy).order_by(Cita.fecha).all()
        
        if not citas:
            return f"No he encontrado ninguna cita futura para el teléfono {telefono}."
            
        info = [f"Día {c.fecha.strftime('%Y-%m-%d')} a las {c.hora.strftime('%H:%M')}" for c in citas]
        return f"Citas encontradas para {telefono}: {'; '.join(info)}."
    except Exception as e:
        return f"Error buscando citas: {e}"

# ia/herramientas.py (Solo te pongo la parte a modificar, el resto déjalo igual)

def reservar_cita_db(fecha, hora, telefono, nombre):
    """Crea una nueva cita asignando al primer peluquero disponible."""
    try:
        fecha_obj = datetime.strptime(fecha, "%Y-%m-%d").date()
        hora_obj = datetime.strptime(hora, "%H:%M").time()
        
        # 1. Obtenemos todos los peluqueros activos de la base de datos
        peluqueros = Peluquero.query.filter_by(activo=True).all()
        peluquero_asignado = None
        
        # 2. Buscamos cuál de ellos está libre a esa hora
        for p in peluqueros:
            ocupado = Cita.query.filter_by(fecha=fecha_obj, hora=hora_obj, peluquero_id=p.id).first()
            if not ocupado:
                peluquero_asignado = p.id
                break # ¡Encontramos uno libre! Paramos de buscar.
                
        # 3. Si todos están ocupados a esa hora
        if not peluquero_asignado:
            return f"Imposible reservar. La hora {hora} ya está totalmente ocupada por todos los peluqueros. Pide al cliente que elija otra hora."
            
        # 4. Crear la cita usando tu modelo con el peluquero asignado
        nueva_cita = Cita(
            fecha=fecha_obj,
            hora=hora_obj,
            servicio="Reserva Asistente IA", 
            peluquero_id=peluquero_asignado,
            nombre_invitado=nombre,
            telefono_cliente=telefono
        )
        db.session.add(nueva_cita)
        db.session.commit()
        return f"¡Éxito! Cita reservada para {nombre} el {fecha} a las {hora}."
    except Exception as e:
        db.session.rollback()
        return f"Hubo un error al guardar la cita: {e}"

# EL MAPA DE HERRAMIENTAS (Actualizado sin pedir peluquero)
herramientas_para_ia = [
    {
        "type": "function",
        "function": {
            "name": "consultar_disponibilidad_db",
            "description": "Consulta qué horas están ocupadas en una fecha específica.",
            "parameters": {
                "type": "object",
                "properties": {"fecha": {"type": "string", "description": "Fecha en formato YYYY-MM-DD"}},
                "required": ["fecha"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "consultar_mis_citas_db",
            "description": "Busca las próximas citas de un cliente usando su número de teléfono.",
            "parameters": {
                "type": "object",
                "properties": {"telefono": {"type": "string", "description": "El número de teléfono del cliente"}},
                "required": ["telefono"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "reservar_cita_db",
            "description": "Reserva una cita firme en la base de datos.",
            "parameters": {
                "type": "object",
                "properties": {
                    "fecha": {"type": "string", "description": "Fecha YYYY-MM-DD"},
                    "hora": {"type": "string", "description": "Hora en formato HH:MM (ejemplo: 17:30)"},
                    "telefono": {"type": "string", "description": "Teléfono de contacto"},
                    "nombre": {"type": "string", "description": "Nombre del cliente"}
                },
                "required": ["fecha", "hora", "telefono", "nombre"] # Eliminado peluquero_id
            }
        }
    }
]