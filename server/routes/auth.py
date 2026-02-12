from flask import Blueprint, request, jsonify, g
import bcrypt
import jwt
import datetime
import os
import functools
from database import get_db

auth_bp = Blueprint('auth', __name__)

SECRET_KEY = os.environ.get('JWT_SECRET', 'lydistories-secret-key-2026')

def create_token(user_id, role):
    payload = {
        'user_id': user_id,
        'role': role,
        'exp': datetime.datetime.utcnow() + datetime.timedelta(days=7)
    }
    return jwt.encode(payload, SECRET_KEY, algorithm='HS256')

def decode_token(token):
    try:
        return jwt.decode(token, SECRET_KEY, algorithms=['HS256'])
    except jwt.ExpiredSignatureError:
        return None
    except jwt.InvalidTokenError:
        return None

def login_required(f):
    @functools.wraps(f)
    def decorated(*args, **kwargs):
        token = request.headers.get('Authorization', '').replace('Bearer ', '')
        if not token:
            return jsonify({'error': 'Authentication required'}), 401
        payload = decode_token(token)
        if not payload:
            return jsonify({'error': 'Invalid or expired token'}), 401
        g.user_id = payload['user_id']
        g.user_role = payload['role']
        return f(*args, **kwargs)
    return decorated

def admin_required(f):
    @functools.wraps(f)
    def decorated(*args, **kwargs):
        token = request.headers.get('Authorization', '').replace('Bearer ', '')
        if not token:
            return jsonify({'error': 'Authentication required'}), 401
        payload = decode_token(token)
        if not payload:
            return jsonify({'error': 'Invalid or expired token'}), 401
        if payload['role'] != 'admin':
            return jsonify({'error': 'Admin access required'}), 403
        g.user_id = payload['user_id']
        g.user_role = payload['role']
        return f(*args, **kwargs)
    return decorated

def optional_auth(f):
    @functools.wraps(f)
    def decorated(*args, **kwargs):
        token = request.headers.get('Authorization', '').replace('Bearer ', '')
        if token:
            payload = decode_token(token)
            if payload:
                g.user_id = payload['user_id']
                g.user_role = payload['role']
            else:
                g.user_id = None
                g.user_role = None
        else:
            g.user_id = None
            g.user_role = None
        return f(*args, **kwargs)
    return decorated

@auth_bp.route('/api/auth/register', methods=['POST'])
def register():
    data = request.get_json()
    name = data.get('name', '').strip()
    email = data.get('email', '').strip().lower()
    password = data.get('password', '')
    
    if not name or not email or not password:
        return jsonify({'error': 'Name, email and password are required'}), 400
    if len(password) < 6:
        return jsonify({'error': 'Password must be at least 6 characters'}), 400
    
    db = get_db()
    existing = db.execute('SELECT id FROM users WHERE email = ?', (email,)).fetchone()
    if existing:
        db.close()
        return jsonify({'error': 'Email already registered'}), 409
    
    pw_hash = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
    cursor = db.execute(
        'INSERT INTO users (name, email, password_hash) VALUES (?, ?, ?)',
        (name, email, pw_hash)
    )
    user_id = cursor.lastrowid
    db.commit()
    
    token = create_token(user_id, 'user')
    user = db.execute('SELECT id, name, email, role, created_at FROM users WHERE id = ?', (user_id,)).fetchone()
    db.close()
    
    return jsonify({
        'token': token,
        'user': dict(user)
    }), 201

@auth_bp.route('/api/auth/login', methods=['POST'])
def login():
    data = request.get_json()
    email = data.get('email', '').strip().lower()
    password = data.get('password', '')
    
    if not email or not password:
        return jsonify({'error': 'Email and password are required'}), 400
    
    db = get_db()
    user = db.execute('SELECT * FROM users WHERE email = ?', (email,)).fetchone()
    db.close()
    
    if not user:
        return jsonify({'error': 'Invalid email or password'}), 401
    
    if not bcrypt.checkpw(password.encode('utf-8'), user['password_hash'].encode('utf-8')):
        return jsonify({'error': 'Invalid email or password'}), 401
    
    token = create_token(user['id'], user['role'])
    
    return jsonify({
        'token': token,
        'user': {
            'id': user['id'],
            'name': user['name'],
            'email': user['email'],
            'role': user['role'],
            'created_at': user['created_at']
        }
    })

@auth_bp.route('/api/auth/me', methods=['GET'])
@login_required
def get_me():
    db = get_db()
    user = db.execute('SELECT id, name, email, role, created_at FROM users WHERE id = ?', (g.user_id,)).fetchone()
    db.close()
    
    if not user:
        return jsonify({'error': 'User not found'}), 404
    
    return jsonify({'user': dict(user)})
