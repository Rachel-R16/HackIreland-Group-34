from flask import Flask, request, jsonify, make_response
from flask_cors import CORS
from uuid import uuid4
from profile import ProfileBuilder

def create_app():
    app = Flask(__name__)

    # Enable CORS for all routes
    CORS(app, 
         supports_credentials=True,
         resources={r"/*": {"origins": "*"}})

    # Store ProfileBuilder instances and conversation history
    sessions = {}

    @app.after_request
    def after_request(response):
        response.headers.add('Access-Control-Allow-Origin', '*')
        response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
        response.headers.add('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE,OPTIONS')
        return response

    @app.route('/start-conversation', methods=['POST', 'OPTIONS'])
    def start_conversation():
        # Handle preflight request
        if request.method == 'OPTIONS':
            response = make_response()
            response.headers.add('Access-Control-Allow-Origin', '*')
            response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
            response.headers.add('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE,OPTIONS')
            return response
        
        # Get mode from request body, default to 'profile' if not specified
        data = request.json or {}
        mode = data.get('mode', 'profile')
            
        session_id = str(uuid4())
        
        # Create new session with ProfileBuilder and empty conversation
        sessions[session_id] = {
            'builder': ProfileBuilder(),
            'conversation': [],
            'mode': mode  # Store the mode in the session
        }
        
        # Get initial message from the profile builder
        session = sessions[session_id]
        ai_response = session['builder'].process_conversation(session['conversation'])
        
        if 'question' in ai_response:
            session['conversation'].append(ai_response['question'])
            return jsonify({
                "session_id": session_id,
                "message": ai_response['question'],
                "completed": False,
                "mode": mode
            })
        else:
            return jsonify({
                "session_id": session_id,
                "profile": ai_response['profile'],
                "completed": True,
                "mode": mode
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
                "completed": False,
                "mode": session['mode']
            })
        else:
            return jsonify({
                "profile": ai_response['profile'],
                "completed": True,
                "mode": session['mode']
            })

    return app

# Create the application instance
app = create_app()

if __name__ == '__main__':
    app.run(debug=True, port=5002, host='0.0.0.0')