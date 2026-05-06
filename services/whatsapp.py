import requests

# services/whatsapp.py

def enviar_whatsapp_recordatorio(telefono, nombre_cliente, hora, peluquero):
    # 1. Normalizar el teléfono
    # Quitamos espacios por si acaso y verificamos longitud
    tel_limpio = str(telefono).replace(" ", "").strip()
    
    if len(tel_limpio) == 9 and tel_limpio.startswith(('6', '7')):
        telefono_final = f"+34{tel_limpio}"
    elif tel_limpio.startswith('34') and len(tel_limpio) == 11:
        telefono_final = f"+{tel_limpio}"
    else:
        # Si ya trae el +, lo dejamos como está
        telefono_final = tel_limpio

    # 2. Tu lógica de envío (Ejemplo con requests)
    print(f"📱 Preparando envío para: {telefono_final}")
    
    # Aquí iría tu llamada a la API
    # payload = {"to": telefono_final, "message": f"Hola {nombre_cliente}..."}

def enviar_whatsapp_recordatorio(telefono, nombre_cliente, hora, peluquero):
    # Ejemplo usando la API de Twilio o Meta
    url = "https://api.tu-proveedor.com/v1/messages"
    payload = {
        "to": f"whatsapp:{telefono}",
        "message": f"Hola {nombre_cliente}, recordatorio de tu cita hoy a las {hora}. ¡Te esperamos! si no puedes venir modifica tu cita"
    }
    headers = {"Authorization": "Bearer TU_TOKEN_AQUÍ"}
    # response = requests.post(url, json=payload) # Descomentar al configurar
    print(f"Enviando recordatorio a {telefono}") # Para pruebas



#Peluquero quitado, se puede añadir al mensaje