from flask import Flask, request, jsonify, make_response
from flask_cors import CORS
from uuid import uuid4
from profile import generate_next_step

app = Flask(__name__)

# Enable CORS for all routes
CORS(app, 
     supports_credentials=True,
     resources={r"/*": {"origins": "*"}})

# Add CORS headers to all responses
@app.after_request
def after_request(response):
    response.headers.add('Access-Control-Allow-Origin', '*')
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
    response.headers.add('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE,OPTIONS')
    return response

conversation_sessions = {}

@app.route('/start-conversation', methods=['POST', 'OPTIONS'])
def start_conversation():
    # Handle preflight request
    if request.method == 'OPTIONS':
        response = make_response()
        response.headers.add('Access-Control-Allow-Origin', '*')
        response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
        response.headers.add('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE,OPTIONS')
        return response
        
    session_id = str(uuid4())
    conversation_sessions[session_id] = []
    # Start with first question
    ai_response = generate_next_step([], session_id)
    if 'question' in ai_response:
        conversation_sessions[session_id].append(f"AI: {ai_response['question']}")
    return jsonify({"session_id": session_id, "response": ai_response})

@app.route('/continue-conversation', methods=['POST', 'OPTIONS'])
def continue_conversation():
    # Handle preflight request
    if request.method == 'OPTIONS':
        response = make_response()
        response.headers.add('Access-Control-Allow-Origin', '*')
        response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
        response.headers.add('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE,OPTIONS')
        return response
        
    data = request.json
    if not data or 'session_id' not in data:
        return jsonify({"error": "Missing session_id"}), 400
        
    session_id = data['session_id']
    user_message = data.get('message', '')
    
    if session_id not in conversation_sessions:
        return jsonify({"error": "Invalid session ID"}), 400
    
    conversation = conversation_sessions[session_id]
    if user_message:
        conversation.append(f"User: {user_message}")
    
    ai_response = generate_next_step(conversation, session_id)
    
    if 'question' in ai_response:
        conversation.append(f"AI: {ai_response['question']}")
    
    return jsonify(ai_response)

if __name__ == '__main__':
    app.run(debug=True, port=5001, host='0.0.0.0')