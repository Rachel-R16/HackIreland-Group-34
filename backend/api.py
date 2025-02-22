from flask import Flask, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app, resources={r"/api/*": {"origins": "http://localhost:3000"}})

@app.route('/api/test')
def test_endpoint():
    return jsonify({'message': 'Test endpoint working!'})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001, debug=True)