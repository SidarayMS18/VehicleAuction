# app.py
from flask import Flask, render_template, session
from database import init_db
from api import api

app = Flask(__name__)
app.secret_key = 'your-secure-secret-key'  # Change this for production

# Initialize the database
init_db()

# Register API blueprint with prefix '/api'
app.register_blueprint(api, url_prefix='/api')

@app.route('/')
def index():
    """Serve the main Vue.js template."""
    current_user = None
    # Since notifications are loaded via the API, we only send user info here.
    if 'user_id' in session:
        current_user = {
            'id': session['user_id'],
            'username': session.get('username'),
            'is_admin': session.get('is_admin', False)
        }
    return render_template('index.html', currentUser=current_user)

if __name__ == '__main__':
    app.run(debug=True)
