from flask import Flask, request, jsonify, make_response
from flask_cors import CORS
from uuid import uuid4
from profile import ProfileBuilder

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

# Store ProfileBuilder instances and conversation history
sessions = {}

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
    
    # Create new session with ProfileBuilder and empty conversation
    sessions[session_id] = {
        'builder': ProfileBuilder(),
        'conversation': []
    }
    
    # Get initial message from the profile builder
    session = sessions[session_id]
    ai_response = session['builder'].process_conversation(session['conversation'])
    
    if 'question' in ai_response:
        session['conversation'].append(ai_response['question'])
        return jsonify({
            "session_id": session_id,
            "message": ai_response['question'],
            "completed": False
        })
    else:
        return jsonify({
            "session_id": session_id,
            "profile": ai_response['profile'],
            "completed": True
        })

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
    
    if session_id not in sessions:
        return jsonify({"error": "Invalid session ID"}), 400
    
    session = sessions[session_id]
    if user_message:
        session['conversation'].append(user_message)
    
    ai_response = session['builder'].process_conversation(session['conversation'])
    
    if 'question' in ai_response:
        session['conversation'].append(ai_response['question'])
        return jsonify({
            "message": ai_response['question'],
            "completed": False
        })
    else:
        return jsonify({
            "profile": ai_response['profile'],
            "completed": True
        })

if __name__ == '__main__':
    app.run(debug=True, port=5001, host='0.0.0.0')