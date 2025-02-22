from flask import Flask, jsonify

app = Flask(__name__)

@app.route('/api/test')
def test_endpoint():
    return jsonify({'message': 'Test endpoint working!'})

if __name__ == '__main__':
    app.run(debug=True)