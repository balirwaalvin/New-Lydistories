from flask import Blueprint, request, jsonify, g
from database import get_db
from routes.auth import login_required, admin_required

users_bp = Blueprint('users', __name__)

# ── Admin endpoints ──

@users_bp.route('/api/users', methods=['GET'])
@admin_required
def list_users():
    db = get_db()
    users = db.execute('SELECT id, name, email, role, created_at FROM users ORDER BY created_at DESC').fetchall()
    db.close()
    return jsonify({'users': [dict(u) for u in users]})

@users_bp.route('/api/users/stats', methods=['GET'])
@admin_required
def get_stats():
    db = get_db()
    total_users = db.execute('SELECT COUNT(*) as c FROM users WHERE role = "user"').fetchone()['c']
    total_content = db.execute('SELECT COUNT(*) as c FROM content').fetchone()['c']
    total_payments = db.execute('SELECT COUNT(*) as c FROM payments WHERE status = "confirmed"').fetchone()['c']
    total_revenue_row = db.execute('SELECT COALESCE(SUM(amount), 0) as r FROM payments WHERE status = "confirmed"').fetchone()
    total_revenue = total_revenue_row['r']
    recent_payments = db.execute('''
        SELECT p.*, u.name as user_name, c.title as content_title
        FROM payments p
        LEFT JOIN users u ON p.user_id = u.id
        LEFT JOIN content c ON p.content_id = c.id
        WHERE p.status = "confirmed"
        ORDER BY p.created_at DESC LIMIT 10
    ''').fetchall()
    db.close()
    
    return jsonify({
        'stats': {
            'total_users': total_users,
            'total_content': total_content,
            'total_payments': total_payments,
            'total_revenue': total_revenue,
            'recent_payments': [dict(p) for p in recent_payments]
        }
    })

@users_bp.route('/api/users/<int:user_id>', methods=['PUT'])
@admin_required
def update_user(user_id):
    data = request.get_json()
    db = get_db()
    
    user = db.execute('SELECT * FROM users WHERE id = ?', (user_id,)).fetchone()
    if not user:
        db.close()
        return jsonify({'error': 'User not found'}), 404
    
    role = data.get('role', user['role'])
    name = data.get('name', user['name'])
    
    db.execute('UPDATE users SET role = ?, name = ? WHERE id = ?', (role, name, user_id))
    db.commit()
    
    updated = db.execute('SELECT id, name, email, role, created_at FROM users WHERE id = ?', (user_id,)).fetchone()
    db.close()
    
    return jsonify({'user': dict(updated)})

@users_bp.route('/api/users/<int:user_id>', methods=['DELETE'])
@admin_required
def delete_user(user_id):
    db = get_db()
    user = db.execute('SELECT * FROM users WHERE id = ?', (user_id,)).fetchone()
    if not user:
        db.close()
        return jsonify({'error': 'User not found'}), 404
    if user['role'] == 'admin':
        db.close()
        return jsonify({'error': 'Cannot delete admin user'}), 400
    
    db.execute('DELETE FROM bookmarks WHERE user_id = ?', (user_id,))
    db.execute('DELETE FROM reading_progress WHERE user_id = ?', (user_id,))
    db.execute('DELETE FROM user_content_access WHERE user_id = ?', (user_id,))
    db.execute('DELETE FROM payments WHERE user_id = ?', (user_id,))
    db.execute('DELETE FROM users WHERE id = ?', (user_id,))
    db.commit()
    db.close()
    
    return jsonify({'message': 'User deleted successfully'})

# ── Bookmarks ──

@users_bp.route('/api/bookmarks', methods=['GET'])
@login_required
def get_bookmarks():
    db = get_db()
    bookmarks = db.execute('''
        SELECT b.id, b.created_at, c.id as content_id, c.title, c.author, c.category,
               c.description, c.cover_image, c.price
        FROM bookmarks b
        JOIN content c ON b.content_id = c.id
        WHERE b.user_id = ?
        ORDER BY b.created_at DESC
    ''', (g.user_id,)).fetchall()
    db.close()
    return jsonify({'bookmarks': [dict(b) for b in bookmarks]})

@users_bp.route('/api/bookmarks', methods=['POST'])
@login_required
def add_bookmark():
    data = request.get_json()
    content_id = data.get('content_id')
    
    if not content_id:
        return jsonify({'error': 'Content ID is required'}), 400
    
    db = get_db()
    try:
        db.execute('INSERT INTO bookmarks (user_id, content_id) VALUES (?, ?)', (g.user_id, content_id))
        db.commit()
    except Exception:
        db.close()
        return jsonify({'error': 'Bookmark already exists'}), 409
    
    db.close()
    return jsonify({'message': 'Bookmark added'}), 201

@users_bp.route('/api/bookmarks/<int:content_id>', methods=['DELETE'])
@login_required
def remove_bookmark(content_id):
    db = get_db()
    db.execute('DELETE FROM bookmarks WHERE user_id = ? AND content_id = ?', (g.user_id, content_id))
    db.commit()
    db.close()
    return jsonify({'message': 'Bookmark removed'})

# ── Reading Progress ──

@users_bp.route('/api/reading-progress', methods=['PUT'])
@login_required
def update_reading_progress():
    data = request.get_json()
    content_id = data.get('content_id')
    progress = data.get('progress_percent', 0)
    last_page = data.get('last_page', 0)
    
    if not content_id:
        return jsonify({'error': 'Content ID is required'}), 400
    
    db = get_db()
    existing = db.execute(
        'SELECT id FROM reading_progress WHERE user_id = ? AND content_id = ?',
        (g.user_id, content_id)
    ).fetchone()
    
    if existing:
        db.execute('''
            UPDATE reading_progress SET progress_percent = ?, last_page = ?, updated_at = CURRENT_TIMESTAMP
            WHERE user_id = ? AND content_id = ?
        ''', (progress, last_page, g.user_id, content_id))
    else:
        db.execute('''
            INSERT INTO reading_progress (user_id, content_id, progress_percent, last_page)
            VALUES (?, ?, ?, ?)
        ''', (g.user_id, content_id, progress, last_page))
    
    db.commit()
    db.close()
    return jsonify({'message': 'Progress updated'})

@users_bp.route('/api/reading-progress/<int:content_id>', methods=['GET'])
@login_required
def get_reading_progress(content_id):
    db = get_db()
    progress = db.execute(
        'SELECT * FROM reading_progress WHERE user_id = ? AND content_id = ?',
        (g.user_id, content_id)
    ).fetchone()
    db.close()
    
    if progress:
        return jsonify({'progress': dict(progress)})
    return jsonify({'progress': None})

# ── User Dashboard ──

@users_bp.route('/api/users/dashboard', methods=['GET'])
@login_required
def user_dashboard():
    db = get_db()
    
    # Get purchased content
    purchased = db.execute('''
        SELECT c.id, c.title, c.author, c.category, c.cover_image, c.page_count,
               rp.progress_percent, rp.last_page
        FROM user_content_access uca
        JOIN content c ON uca.content_id = c.id
        LEFT JOIN reading_progress rp ON rp.content_id = c.id AND rp.user_id = ?
        WHERE uca.user_id = ?
        ORDER BY uca.granted_at DESC
    ''', (g.user_id, g.user_id)).fetchall()
    
    # Get bookmarks count
    bookmarks_count = db.execute('SELECT COUNT(*) as c FROM bookmarks WHERE user_id = ?', (g.user_id,)).fetchone()['c']
    
    # Get total spent
    total_spent_row = db.execute(
        'SELECT COALESCE(SUM(amount), 0) as t FROM payments WHERE user_id = ? AND status = "confirmed"',
        (g.user_id,)
    ).fetchone()
    total_spent = total_spent_row['t']
    
    db.close()
    
    return jsonify({
        'purchased_content': [dict(p) for p in purchased],
        'bookmarks_count': bookmarks_count,
        'total_spent': total_spent,
        'total_purchased': len(purchased)
    })
