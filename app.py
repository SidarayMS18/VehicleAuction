from flask import Flask, send_file, session
from database import init_db
from api import api
import os

app = Flask(__name__, static_folder='.', static_url_path='')
app.secret_key = os.urandom(24)
app.register_blueprint(api, url_prefix='/api')

init_db()

@app.route('/')
def index():
    return send_file('index.html')

if __name__ == '__main__':
    app.run(debug=False)
