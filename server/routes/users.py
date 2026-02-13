from flask import Blueprint, request, jsonify, g
from database import get_db
from routes.auth import login_required, admin_required
import psycopg2.extras

users_bp = Blueprint('users', __name__)

# ── Admin endpoints ──

@users_bp.route('/api/users', methods=['GET'])
@admin_required
def list_users():
    conn = get_db()
    cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    cur.execute('SELECT id, name, email, role, created_at FROM users ORDER BY created_at DESC')
    users = cur.fetchall()
    cur.close()
    conn.close()
    for u in users:
        u['created_at'] = str(u['created_at'])
    return jsonify({'users': [dict(u) for u in users]})

@users_bp.route('/api/users/stats', methods=['GET'])
@admin_required
def get_stats():
    conn = get_db()
    cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)

    cur.execute("SELECT COUNT(*) as c FROM users WHERE role = 'user'")
    total_users = cur.fetchone()['c']

    cur.execute('SELECT COUNT(*) as c FROM content')
    total_content = cur.fetchone()['c']

    cur.execute("SELECT COUNT(*) as c FROM payments WHERE status = 'confirmed'")
    total_payments = cur.fetchone()['c']

    cur.execute("SELECT COALESCE(SUM(amount), 0) as r FROM payments WHERE status = 'confirmed'")
    total_revenue = cur.fetchone()['r']

    cur.execute('''
        SELECT p.*, u.name as user_name, c.title as content_title
        FROM payments p
        LEFT JOIN users u ON p.user_id = u.id
        LEFT JOIN content c ON p.content_id = c.id
        WHERE p.status = 'confirmed'
        ORDER BY p.created_at DESC LIMIT 10
    ''')
    recent_payments = cur.fetchall()
    cur.close()
    conn.close()

    for p in recent_payments:
        if 'created_at' in p and p['created_at']:
            p['created_at'] = str(p['created_at'])

    return jsonify({
        'stats': {
            'total_users': total_users,
            'total_content': total_content,
            'total_payments': total_payments,
            'total_revenue': float(total_revenue),
            'recent_payments': [dict(p) for p in recent_payments]
        }
    })

@users_bp.route('/api/users/<int:user_id>', methods=['PUT'])
@admin_required
def update_user(user_id):
    data = request.get_json()
    conn = get_db()
    cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)

    cur.execute('SELECT * FROM users WHERE id = %s', (user_id,))
    user = cur.fetchone()
    if not user:
        cur.close()
        conn.close()
        return jsonify({'error': 'User not found'}), 404

    role = data.get('role', user['role'])
    name = data.get('name', user['name'])

    cur.execute('UPDATE users SET role = %s, name = %s WHERE id = %s', (role, name, user_id))
    conn.commit()

    cur.execute('SELECT id, name, email, role, created_at FROM users WHERE id = %s', (user_id,))
    updated = cur.fetchone()
    cur.close()
    conn.close()

    updated['created_at'] = str(updated['created_at'])
    return jsonify({'user': dict(updated)})

@users_bp.route('/api/users/<int:user_id>', methods=['DELETE'])
@admin_required
def delete_user(user_id):
    conn = get_db()
    cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)

    cur.execute('SELECT * FROM users WHERE id = %s', (user_id,))
    user = cur.fetchone()
    if not user:
        cur.close()
        conn.close()
        return jsonify({'error': 'User not found'}), 404
    if user['role'] == 'admin':
        cur.close()
        conn.close()
        return jsonify({'error': 'Cannot delete admin user'}), 400

    cur.execute('DELETE FROM bookmarks WHERE user_id = %s', (user_id,))
    cur.execute('DELETE FROM reading_progress WHERE user_id = %s', (user_id,))
    cur.execute('DELETE FROM user_content_access WHERE user_id = %s', (user_id,))
    cur.execute('DELETE FROM payments WHERE user_id = %s', (user_id,))
    cur.execute('DELETE FROM users WHERE id = %s', (user_id,))
    conn.commit()
    cur.close()
    conn.close()

    return jsonify({'message': 'User deleted successfully'})

# ── Bookmarks ──

@users_bp.route('/api/bookmarks', methods=['GET'])
@login_required
def get_bookmarks():
    conn = get_db()
    cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    cur.execute('''
        SELECT b.id, b.created_at, c.id as content_id, c.title, c.author, c.category,
               c.description, c.cover_image, c.price
        FROM bookmarks b
        JOIN content c ON b.content_id = c.id
        WHERE b.user_id = %s
        ORDER BY b.created_at DESC
    ''', (g.user_id,))
    bookmarks = cur.fetchall()
    cur.close()
    conn.close()

    for b in bookmarks:
        if 'created_at' in b and b['created_at']:
            b['created_at'] = str(b['created_at'])

    return jsonify({'bookmarks': [dict(b) for b in bookmarks]})

@users_bp.route('/api/bookmarks', methods=['POST'])
@login_required
def add_bookmark():
    data = request.get_json()
    content_id = data.get('content_id')

    if not content_id:
        return jsonify({'error': 'Content ID is required'}), 400

    conn = get_db()
    cur = conn.cursor()
    try:
        cur.execute('INSERT INTO bookmarks (user_id, content_id) VALUES (%s, %s)', (g.user_id, content_id))
        conn.commit()
    except Exception:
        conn.rollback()
        cur.close()
        conn.close()
        return jsonify({'error': 'Bookmark already exists'}), 409

    cur.close()
    conn.close()
    return jsonify({'message': 'Bookmark added'}), 201

@users_bp.route('/api/bookmarks/<int:content_id>', methods=['DELETE'])
@login_required
def remove_bookmark(content_id):
    conn = get_db()
    cur = conn.cursor()
    cur.execute('DELETE FROM bookmarks WHERE user_id = %s AND content_id = %s', (g.user_id, content_id))
    conn.commit()
    cur.close()
    conn.close()
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

    conn = get_db()
    cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    cur.execute(
        'SELECT id FROM reading_progress WHERE user_id = %s AND content_id = %s',
        (g.user_id, content_id)
    )
    existing = cur.fetchone()

    if existing:
        cur.execute('''
            UPDATE reading_progress SET progress_percent = %s, last_page = %s, updated_at = CURRENT_TIMESTAMP
            WHERE user_id = %s AND content_id = %s
        ''', (progress, last_page, g.user_id, content_id))
    else:
        cur.execute('''
            INSERT INTO reading_progress (user_id, content_id, progress_percent, last_page)
            VALUES (%s, %s, %s, %s)
        ''', (g.user_id, content_id, progress, last_page))

    conn.commit()
    cur.close()
    conn.close()
    return jsonify({'message': 'Progress updated'})

@users_bp.route('/api/reading-progress/<int:content_id>', methods=['GET'])
@login_required
def get_reading_progress(content_id):
    conn = get_db()
    cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    cur.execute(
        'SELECT * FROM reading_progress WHERE user_id = %s AND content_id = %s',
        (g.user_id, content_id)
    )
    progress = cur.fetchone()
    cur.close()
    conn.close()

    if progress:
        if 'updated_at' in progress and progress['updated_at']:
            progress['updated_at'] = str(progress['updated_at'])
        return jsonify({'progress': dict(progress)})
    return jsonify({'progress': None})

# ── User Dashboard ──

@users_bp.route('/api/users/dashboard', methods=['GET'])
@login_required
def user_dashboard():
    conn = get_db()
    cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)

    # Get purchased content
    cur.execute('''
        SELECT c.id, c.title, c.author, c.category, c.cover_image, c.page_count,
               rp.progress_percent, rp.last_page
        FROM user_content_access uca
        JOIN content c ON uca.content_id = c.id
        LEFT JOIN reading_progress rp ON rp.content_id = c.id AND rp.user_id = %s
        WHERE uca.user_id = %s
        ORDER BY uca.granted_at DESC
    ''', (g.user_id, g.user_id))
    purchased = cur.fetchall()

    # Get bookmarks count
    cur.execute('SELECT COUNT(*) as c FROM bookmarks WHERE user_id = %s', (g.user_id,))
    bookmarks_count = cur.fetchone()['c']

    # Get total spent
    cur.execute(
        "SELECT COALESCE(SUM(amount), 0) as t FROM payments WHERE user_id = %s AND status = 'confirmed'",
        (g.user_id,)
    )
    total_spent = cur.fetchone()['t']

    cur.close()
    conn.close()

    return jsonify({
        'purchased_content': [dict(p) for p in purchased],
        'bookmarks_count': bookmarks_count,
        'total_spent': float(total_spent),
        'total_purchased': len(purchased)
    })
