from flask import Flask, send_from_directory, jsonify
from flask_cors import CORS
import os
from dotenv import load_dotenv

load_dotenv()

from database import init_db
from routes.auth import auth_bp
from routes.content import content_bp
from routes.payments import payments_bp
from routes.users import users_bp
from routes.profile import profile_bp

app = Flask(__name__)
app.config['MAX_CONTENT_LENGTH'] = 10 * 1024 * 1024  # 10 MB max upload
CORS(app, resources={r"/api/*": {"origins": "*"}})

# Register blueprints
app.register_blueprint(auth_bp)
app.register_blueprint(content_bp)
app.register_blueprint(payments_bp)
app.register_blueprint(users_bp)
app.register_blueprint(profile_bp)

# Serve uploaded files
UPLOAD_DIR = os.path.join(os.path.dirname(__file__), 'uploads')
os.makedirs(UPLOAD_DIR, exist_ok=True)

@app.route('/uploads/<path:filename>')
def serve_upload(filename):
    return send_from_directory(UPLOAD_DIR, filename)

@app.route('/api/health')
def health():
    return {'status': 'ok', 'app': 'Lydistories API'}

# ── Serve React frontend ──
# The built React app lives in ../dist (one level up from server/)
DIST_DIR = os.path.join(os.path.dirname(__file__), '..', 'dist')
DIST_DIR = os.path.abspath(DIST_DIR)

@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def serve_frontend(path):
    """Serve the React app. API routes are handled by blueprints above."""
    # If the requested file exists in dist, serve it
    if path and os.path.exists(os.path.join(DIST_DIR, path)):
        return send_from_directory(DIST_DIR, path)
    # Otherwise serve index.html (for React Router client-side routing)
    return send_from_directory(DIST_DIR, 'index.html')

# Initialize database tables on startup
init_db()

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    print(f"\n Lydistories running on http://localhost:{port}\n")
    app.run(debug=True, host='0.0.0.0', port=port)
