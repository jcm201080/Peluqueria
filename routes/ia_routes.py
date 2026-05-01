# routes/ia_routes.py
from flask import Blueprint, request, jsonify
from ia.consultor import obtener_respuesta_ia

# 1. Definimos el Blueprint
ia_bp = Blueprint('ia', __name__)

# 2. AQUÍ ESTÁ EL CAMBIO: Usamos @ia_bp en lugar de @app
@ia_bp.route('/api/ia/chat', methods=['POST'])
def chat_api():
    data = request.get_json()
    mensaje = data.get('mensaje')
    
    if not mensaje:
        return jsonify({'respuesta': 'Por favor, escribe un mensaje.'}), 400
        
    respuesta_bot = obtener_respuesta_ia(mensaje)
    return jsonify({'respuesta': respuesta_bot})