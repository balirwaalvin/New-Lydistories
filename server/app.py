from flask import Flask, send_from_directory
from flask_cors import CORS
import os

from database import init_db
from routes.auth import auth_bp
from routes.content import content_bp
from routes.payments import payments_bp
from routes.users import users_bp

app = Flask(__name__)
CORS(app, resources={r"/api/*": {"origins": "*"}})

# Register blueprints
app.register_blueprint(auth_bp)
app.register_blueprint(content_bp)
app.register_blueprint(payments_bp)
app.register_blueprint(users_bp)

# Serve uploaded files
UPLOAD_DIR = os.path.join(os.path.dirname(__file__), 'uploads')
os.makedirs(UPLOAD_DIR, exist_ok=True)

@app.route('/uploads/<path:filename>')
def serve_upload(filename):
    return send_from_directory(UPLOAD_DIR, filename)

@app.route('/api/health')
def health():
    return {'status': 'ok', 'app': 'Lydistories API'}

# Initialize database tables on startup (works with both gunicorn and flask run)
init_db()

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    print(f"\n🔥 Lydistories API running on http://localhost:{port}\n")
    app.run(debug=True, host='0.0.0.0', port=port)
