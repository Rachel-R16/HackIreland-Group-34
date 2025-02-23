from flask import Flask, request, jsonify, make_response
from flask_cors import CORS
from uuid import uuid4
import json
from openai import OpenAI
from recommendations import recommend
import json
from profile import ProfileBuilder

app = Flask(__name__)

CORS(app, 
     supports_credentials=True,
     resources={r"/*": {"origins": "*"}})

# Add CORS headers to all responses
@app.after_request
def after_request(response):
    origin = request.headers.get("Origin")
    if origin:
        response.headers["Access-Control-Allow-Origin"] = origin
    response.headers["Access-Control-Allow-Headers"] = "Content-Type,Authorization"
    response.headers["Access-Control-Allow-Methods"] = "GET,PUT,POST,DELETE,OPTIONS"
    return response

# Store ProfileBuilder instances and conversation history
sessions = {}

def handle_options():
    """Handles CORS preflight requests."""
    response = make_response()
    response.headers.add("Access-Control-Allow-Origin", "*")
    response.headers.add("Access-Control-Allow-Headers", "Content-Type,Authorization")
    response.headers.add("Access-Control-Allow-Methods", "GET,PUT,POST,DELETE,OPTIONS")
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

    data = request.json
    if not data or 'profile_type' not in data:
        return jsonify({"error": "Missing profile_type"}), 400

    profile_type = data['profile_type']
    session_id = str(uuid4())

    try:
        # Create new session with ProfileBuilder and empty conversation
        sessions[session_id] = {
            'builder': ProfileBuilder(profile_type),
            'conversation': [],
            'profile_type': profile_type
        }

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

    except ValueError as e:
        return jsonify({"error": str(e)}), 400


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


@app.route('/recommend', methods=['POST', 'OPTIONS'])
def recommend_api():
    """
    This endpoint is used to call the recommend function with the given data.
    
    Parameters:
    data (dict): A dictionary containing the user's preferences and other relevant information.
    
    Returns:
    A JSON object containing the recommended universities and courses.
    """
    if request.method == 'OPTIONS':
        return handle_options()
    
    data = request.json
    if not data or "data" not in data or "profile_type" not in data:
        return jsonify({"error": "Invalid input data"}), 400

    # Load JSON Data
    with open('data/country-university-dataset.json', 'r') as f:
        country_university_data = json.load(f)
    print("done here")
    with open('data/university-course-dataset.json', 'r') as f:
        university_course_data = json.load(f)
    with open('data/university-accommodation-dataset.json', 'r') as f:
        university_accommodation_data = json.load(f)
    
    print("done here too")
    # Call the recommend_courses function
    recommendations = recommend(data, country_university_data, university_course_data, university_accommodation_data)
    print(recommendations)
    return jsonify({"recommendations": recommendations})


if __name__ == '__main__':
    app.run(debug=True, port=5000, host='0.0.0.0')