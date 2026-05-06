import requests

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