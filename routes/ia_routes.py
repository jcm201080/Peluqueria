# routes/ia_routes.py
from flask import Blueprint, request, jsonify
from ia.consultor import obtener_respuesta_ia
import traceback

ia_bp = Blueprint('ia', __name__)

@ia_bp.route('/api/ia/chat', methods=['POST'])
def chat_api():
    data = request.get_json()
    mensaje = data.get('mensaje')
    
    # Leemos la URL actual del usuario (nos la mandará el JS)
    url_actual = data.get('url', '')
    
    # Comprobamos si la palabra 'contacto' está en la ruta
    en_contacto = '/contacto' in url_actual
    
    if not mensaje:
        return jsonify({'respuesta': 'Por favor, escribe un mensaje.'}), 400
        
    try:
        # Le pasamos la variable a nuestra IA
        respuesta_bot = obtener_respuesta_ia(mensaje, en_pagina_contacto=en_contacto)
        return jsonify({'respuesta': respuesta_bot})
        
    except Exception as e:
        print(f"❌ ERROR CRÍTICO EN IA: {str(e)}")
        traceback.print_exc() 
        return jsonify({
            'respuesta': "⚠️ Ups, error técnico en el servidor. Por favor, inténtalo de nuevo."
        }), 500