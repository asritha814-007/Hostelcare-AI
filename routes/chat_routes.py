from flask import Blueprint, request, jsonify
from nlp.chatbot_engine import ChatbotEngine

chat_bp = Blueprint('chat', __name__)
chatbot = ChatbotEngine()

@chat_bp.route('/api/chat', methods=['POST'])
def chat():
    data = request.get_json() or {}
    message = data.get('message', '').strip()
    session_id = data.get('session_id', 'default_session').strip()

    if not message:
        return jsonify({
            "success": False,
            "error": "Empty message"
        }), 400

    result = chatbot.process_message(message, session_id=session_id)
    return jsonify({
        "success": True,
        "data": result
    })

@chat_bp.route('/api/chat/reset', methods=['POST'])
def reset_chat():
    data = request.get_json() or {}
    session_id = data.get('session_id', 'default_session').strip()
    chatbot.reset_session(session_id)
    return jsonify({
        "success": True,
        "message": "Conversation history reset successfully"
    })
