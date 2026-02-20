from flask import Blueprint, request, jsonify, g, current_app
from database import get_db
from routes.auth import login_required
import psycopg2.extras
import bcrypt
import os
import uuid

profile_bp = Blueprint('profile', __name__)

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp'}
MAX_FILE_SIZE = 5 * 1024 * 1024  # 5 MB

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@profile_bp.route('/api/profile', methods=['PUT'])
@login_required
def update_profile():
    """Update name and optionally change password."""
    data = request.get_json()
    name = (data.get('name') or '').strip()
    current_password = data.get('current_password')
    new_password = data.get('new_password')

    if not name:
        return jsonify({'error': 'Name is required'}), 400

    conn = get_db()
    cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    cur.execute('SELECT * FROM users WHERE id = %s', (g.user_id,))
    user = cur.fetchone()

    if not user:
        cur.close(); conn.close()
        return jsonify({'error': 'User not found'}), 404

    # Handle password change
    new_hash = user['password_hash']
    if new_password:
        if not current_password:
            cur.close(); conn.close()
            return jsonify({'error': 'Current password is required to set a new password'}), 400
        if not bcrypt.checkpw(current_password.encode('utf-8'), user['password_hash'].encode('utf-8')):
            cur.close(); conn.close()
            return jsonify({'error': 'Current password is incorrect'}), 401
        if len(new_password) < 6:
            cur.close(); conn.close()
            return jsonify({'error': 'New password must be at least 6 characters'}), 400
        new_hash = bcrypt.hashpw(new_password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

    cur.execute(
        'UPDATE users SET name = %s, password_hash = %s WHERE id = %s',
        (name, new_hash, g.user_id)
    )
    conn.commit()

    cur.execute(
        'SELECT id, name, email, role, avatar_url, created_at FROM users WHERE id = %s',
        (g.user_id,)
    )
    updated = cur.fetchone()
    cur.close(); conn.close()

    updated['created_at'] = str(updated['created_at'])
    return jsonify({'message': 'Profile updated successfully', 'user': dict(updated)})


@profile_bp.route('/api/profile/avatar', methods=['POST'])
@login_required
def upload_avatar():
    """Upload a profile picture."""
    if 'avatar' not in request.files:
        return jsonify({'error': 'No file uploaded'}), 400

    file = request.files['avatar']
    if file.filename == '':
        return jsonify({'error': 'No file selected'}), 400

    if not allowed_file(file.filename):
        return jsonify({'error': 'Invalid file type. Only PNG, JPG, GIF, WEBP allowed.'}), 400

    # Check file size
    file.seek(0, 2)
    size = file.tell()
    file.seek(0)
    if size > MAX_FILE_SIZE:
        return jsonify({'error': 'File too large. Maximum size is 5MB.'}), 400

    # Save with a unique filename
    ext = file.filename.rsplit('.', 1)[1].lower()
    filename = f"avatar_{g.user_id}_{uuid.uuid4().hex[:8]}.{ext}"

    upload_folder = os.path.join(current_app.root_path, 'uploads', 'avatars')
    os.makedirs(upload_folder, exist_ok=True)

    # Remove old avatar file if it exists
    conn = get_db()
    cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    cur.execute('SELECT avatar_url FROM users WHERE id = %s', (g.user_id,))
    row = cur.fetchone()
    if row and row['avatar_url']:
        old_path = os.path.join(current_app.root_path, row['avatar_url'].lstrip('/'))
        if os.path.exists(old_path):
            try:
                os.remove(old_path)
            except Exception:
                pass

    file_path = os.path.join(upload_folder, filename)
    file.save(file_path)

    avatar_url = f'/uploads/avatars/{filename}'

    cur.execute('UPDATE users SET avatar_url = %s WHERE id = %s', (avatar_url, g.user_id))
    conn.commit()
    cur.close(); conn.close()

    return jsonify({'message': 'Avatar uploaded successfully', 'avatar_url': avatar_url})
