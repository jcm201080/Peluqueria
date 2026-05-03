# ia/consultor.py
import os
import requests
import json
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

GROQ_API_KEY = os.getenv("GROQ_API_KEY")

def obtener_respuesta_ia(mensaje_usuario, en_pagina_contacto=False):
    if not GROQ_API_KEY:
        return "Error de configuración. (Clave no encontrada)"

    url = "https://api.groq.com/openai/v1/chat/completions"
    headers = {"Authorization": f"Bearer {GROQ_API_KEY}", "Content-Type": "application/json"}
    
    hoy = datetime.now().strftime("%Y-%m-%d")
    
    # Unificamos Horarios y Reservas dependiendo de la página
    if en_pagina_contacto:
        instruccion_horarios_reservas = (
            "Ya estás en la página correcta. En el calendario puedes ver nuestros horarios de los próximos 15 días. "
            "Busca los días en color verde, eso significa que estamos abiertos. "
            "Para reservar, solo tienes que escribir tu nombre, teléfono, elegir el servicio, tocar un día verde y seleccionar la hora que mejor te venga. "
            "Si necesitas una cita para más adelante (fuera de estos 15 días), por favor contáctanos directamente por WhatsApp."
        )
    else:
        instruccion_horarios_reservas = (
            "Para ver nuestros horarios y reservar, por favor ve a nuestra <a href='https://peluqueria.jesuscmweb.com/contacto' target='_blank' class='chat-link'>Sección Contacto</a>. "
            "Allí verás el calendario con los próximos 15 días. Los días marcados en verde indican que estamos abiertos. "
            "Solo tienes que rellenar tus datos, elegir un servicio, y seleccionar un día verde y una hora. "
            "Si buscas una fecha más lejana a 15 días, escríbenos por WhatsApp."
        )

    mensajes = [
        {
            "role": "system", 
            "content": (
                f"Eres el asistente de Parra-Barber en Fuentes de León. Hoy es {hoy}.\n"
                "📍 UBICACIÓN: Calle Artesanos s/n, CP 06280, Fuentes de León (Badajoz).\n"
                "✂️ SERVICIOS: Corte de pelo, Barba, Infantil, Afeitado clásico.\n\n"
                "⚠️ REGLAS ESTRICTAS:\n"
                "1. DIRECCIÓN: Si preguntan dónde estáis, da la dirección exacta.\n"
                f"2. HORARIOS Y RESERVAS: Si te preguntan por el horario, cuándo abrís, disponibilidad o quieren reservar, responde EXACTAMENTE con esto:\n{instruccion_horarios_reservas}\n"
                "3. GESTIÓN DE CITAS: Si quieren buscar, modificar o cancelar una cita, explícales que deben ir a la sección 'Mis Reservas'. Si tienen cuenta y están dentro, les aparecerán sus citas con la opción de modificar o anular.\n"
                "4. NO PIDAS DATOS: No pidas el número de teléfono ni intentes gestionar tú las citas desde este chat.\n"
                "5. TONO: Sé directo, amable y profesional. NUNCA digas frases robóticas como 'Lo siento, no puedo proporcionar información'."
            )
        },
        {"role": "user", "content": mensaje_usuario}
    ]
    
    try:
        response = requests.post(url, headers=headers, json={
            "model": "llama-3.1-8b-instant",
            "messages": mensajes,
            "temperature": 0.2 # Mantenemos baja la temperatura para que no se invente nada
        })
        
        datos = response.json()
        return datos["choices"][0]["message"]["content"]

    except Exception as e:
        print(f"Error IA: {e}")
        return "Lo siento, tengo un problema técnico. Por favor, utiliza el menú de la web para ir a Contacto y gestionar tu cita o ver los horarios."