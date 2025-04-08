from flask import Flask, send_from_directory
from flask_cors import CORS
from api import api  # Import your Blueprint
import os

app = Flask(__name__, static_folder='.', template_folder='.')
CORS(app)

# Secret key for session management
app.secret_key = 'your-secret-key-here'  # Change this to a secure random key in production

# Register the API blueprint
app.register_blueprint(api, url_prefix='/api')

# Serve index.html on root
@app.route('/')
def index():
    return send_from_directory('.', 'index.html')

# Serve other static files
@app.route('/<path:filename>')
def serve_static(filename):
    return send_from_directory('.', filename)

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)

