from flask import Flask, jsonify

# Create a Flask application
app = Flask(__name__)

# Define a simple endpoint
@app.route('/')
def hello_world():
    return jsonify(message="Hello, World!")

if __name__ == '__main__':
    app.run(debug=True)
