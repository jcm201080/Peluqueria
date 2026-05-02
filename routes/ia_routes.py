# routes/ia_routes.py
from flask import Blueprint, request, jsonify
from ia.consultor import obtener_respuesta_ia
import traceback # Añadimos esto para ver el error completo

# 1. Definimos el Blueprint
ia_bp = Blueprint('ia', __name__)

@ia_bp.route('/api/ia/chat', methods=['POST'])
def chat_api():
    data = request.get_json()
    mensaje = data.get('mensaje')
    
    if not mensaje:
        return jsonify({'respuesta': 'Por favor, escribe un mensaje.'}), 400
        
    try:
        # Intentamos obtener la respuesta
        respuesta_bot = obtener_respuesta_ia(mensaje)
        return jsonify({'respuesta': respuesta_bot})
        
    except Exception as e:
        # 1. Imprimimos el error exacto en la consola del VPS (Logs)
        print(f"❌ ERROR CRÍTICO EN IA: {str(e)}")
        traceback.print_exc() 
        
        # 2. Devolvemos el error al frontend para que no se quede colgado
        return jsonify({
            'respuesta': f"⚠️ Ups, error técnico en el servidor: {str(e)}. Revisa los logs del VPS."
        }), 500