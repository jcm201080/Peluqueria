# ia/consultor.py
import os
import requests
import json
from datetime import datetime

GROQ_API_KEY = os.getenv("GROQ_API_KEY")

def obtener_respuesta_ia(mensaje_usuario):
    if not GROQ_API_KEY:
        return "Error de configuración."

    url = "https://api.groq.com/openai/v1/chat/completions"
    headers = {"Authorization": f"Bearer {GROQ_API_KEY}", "Content-Type": "application/json"}
    
    hoy = datetime.now().strftime("%Y-%m-%d")
    
    mensajes = [
        {
            "role": "system", 
            "content": (
                f"Eres el asistente de Parra-Barber en Fuentes de León. Hoy es {hoy}.\n"
                "📍 UBICACIÓN: Calle Artesanos s/n, CP 06280, Fuentes de León (Badajoz).\n"
                "✂️ SERVICIOS: Corte de pelo, Barba, Infantil, Afeitado clásico.\n\n"
                "⚠️ REGLAS ESTRICTAS:\n"
                "1. DIRECCIÓN: Si preguntan dónde estáis, da la dirección exacta.\n"
                "2. DISPONIBILIDAD Y CITAS: No intentes dar horas ni reservar tú. Indica al cliente que vaya a la página de Contacto para ver huecos, gestionar sus reservas o pedir cita.\n"
                "3. ENLACE: Responde SIEMPRE usando este enlace HTML para las citas: <a href='https://peluqueria.jesuscmweb.com/contacto' class='chat-link'>Sección Contacto</a>.\n"
                "4. INDICACIONES: Explica que en Contacto debe poner su Nombre, Teléfono, elegir el Servicio, Fecha y Hora.\n"
                "5. CUENTAS: Recomienda crear cuenta para mayor rapidez en futuras citas.\n"
                "6. NUNCA menciones funciones internas como 'consultar_disponibilidad_db'."
            )
        },
        {"role": "user", "content": mensaje_usuario}
    ]
    
    try:
        response = requests.post(url, headers=headers, json={
            "model": "llama-3.1-8b-instant",
            "messages": mensajes,
            "temperature": 0.5 # Bajamos la temperatura para que sea más predecible
        })
        
        datos = response.json()
        return datos["choices"][0]["message"]["content"]

    except Exception as e:
        print(f"Error IA: {e}")
        return "Lo siento, para ver la disponibilidad y reservar cita, por favor visita nuestra <a href='https://peluqueria.jesuscmweb.com/contacto'>página de contacto</a>."