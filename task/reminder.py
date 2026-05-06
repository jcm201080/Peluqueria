# tasks/reminder.py
from datetime import datetime
from app import app
from database.models import db, Cita, Peluquero

def ejecutar_recordatorios():
    with app.app_context():
        # Obtenemos la fecha de hoy (o mañana si quieres avisar con 24h)
        hoy = datetime.now().date()
        
        # Filtramos citas de hoy
        citas_hoy = Cita.query.filter_by(fecha=hoy).all()
        
        for cita in citas_hoy:
            # Usamos el teléfono directo de la cita para mayor seguridad
            telefono = cita.telefono_cliente 
            # Obtenemos el nombre (del invitado o del usuario registrado)
            nombre = cita.nombre_invitado if cita.nombre_invitado else cita.cliente_rel.nombre
            # El nombre del peluquero asignado
            barbero = cita.peluquero_rel.nombre
            # Hora en formato HH:MM
            hora_str = cita.hora.strftime('%H:%M')

            # Llamada al servicio de WhatsApp
            from services.whatsapp import enviar_whatsapp
            enviar_whatsapp(telefono, nombre, hora_str, barbero)

if __name__ == "__main__":
    ejecutar_recordatorios()