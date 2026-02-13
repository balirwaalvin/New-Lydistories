from flask import Blueprint, request, jsonify, g
import os
from database import get_db
from routes.auth import login_required, admin_required, optional_auth
from PyPDF2 import PdfReader
import psycopg2.extras

content_bp = Blueprint('content', __name__)

UPLOAD_DIR = os.path.join(os.path.dirname(__file__), '..', 'uploads')
UPLOAD_DIR = os.path.abspath(UPLOAD_DIR)
os.makedirs(UPLOAD_DIR, exist_ok=True)

def _serialize_content(row):
    """Convert a content row dict so all values are JSON-serializable."""
    d = dict(row)
    for key in ('created_at', 'updated_at'):
        if key in d and d[key] is not None:
            d[key] = str(d[key])
    return d

@content_bp.route('/api/content', methods=['GET'])
@optional_auth
def list_content():
    category = request.args.get('category', '')
    search = request.args.get('search', '')
    featured = request.args.get('featured', '')

    conn = get_db()
    cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    query = 'SELECT id, title, author, category, description, preview_text, cover_image, page_count, price, is_featured, created_at FROM content WHERE 1=1'
    params = []

    if category:
        query += ' AND category = %s'
        params.append(category)
    if search:
        query += ' AND (title ILIKE %s OR author ILIKE %s OR description ILIKE %s)'
        params.extend([f'%{search}%'] * 3)
    if featured:
        query += ' AND is_featured = TRUE'

    query += ' ORDER BY created_at DESC'

    cur.execute(query, params)
    rows = cur.fetchall()
    content_list = [_serialize_content(row) for row in rows]

    # Check user access for each content item
    if g.user_id:
        for item in content_list:
            cur.execute(
                'SELECT id FROM user_content_access WHERE user_id = %s AND content_id = %s',
                (g.user_id, item['id'])
            )
            access = cur.fetchone()
            item['has_access'] = access is not None
            if g.user_role == 'admin':
                item['has_access'] = True
    else:
        for item in content_list:
            item['has_access'] = False

    cur.close()
    conn.close()
    return jsonify({'content': content_list})

@content_bp.route('/api/content/<int:content_id>', methods=['GET'])
@optional_auth
def get_content(content_id):
    conn = get_db()
    cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    cur.execute('SELECT * FROM content WHERE id = %s', (content_id,))
    item = cur.fetchone()

    if not item:
        cur.close()
        conn.close()
        return jsonify({'error': 'Content not found'}), 404

    result = _serialize_content(item)
    has_access = False

    if g.user_id:
        cur.execute(
            'SELECT id FROM user_content_access WHERE user_id = %s AND content_id = %s',
            (g.user_id, content_id)
        )
        access = cur.fetchone()
        has_access = access is not None
        if g.user_role == 'admin':
            has_access = True

    result['has_access'] = has_access

    if not has_access:
        result.pop('full_text', None)
        result.pop('file_path', None)

    cur.close()
    conn.close()
    return jsonify({'content': result})

@content_bp.route('/api/content', methods=['POST'])
@admin_required
def create_content():
    title = request.form.get('title', '').strip()
    author = request.form.get('author', 'Unknown').strip()
    category = request.form.get('category', 'article')
    description = request.form.get('description', '').strip()
    preview_text = request.form.get('preview_text', '').strip()
    price = float(request.form.get('price', 5000))
    is_featured = request.form.get('is_featured', '0') in ('1', 'true', 'True')

    if not title:
        return jsonify({'error': 'Title is required'}), 400

    full_text = ''
    file_path = None
    page_count = 0

    # Handle PDF upload
    if 'pdf_file' in request.files:
        pdf_file = request.files['pdf_file']
        if pdf_file.filename:
            filename = f"{title.replace(' ', '_').lower()}_{os.urandom(4).hex()}.pdf"
            filepath = os.path.join(UPLOAD_DIR, filename)
            pdf_file.save(filepath)
            file_path = filename

            try:
                reader = PdfReader(filepath)
                page_count = len(reader.pages)
                text_parts = []
                for page in reader.pages:
                    text = page.extract_text()
                    if text:
                        text_parts.append(text)
                full_text = '\n\n'.join(text_parts)

                if not preview_text and full_text:
                    preview_text = full_text[:500] + '...'
            except Exception as e:
                print(f"PDF extraction error: {e}")

    # Handle cover image
    cover_image = None
    if 'cover_image' in request.files:
        img_file = request.files['cover_image']
        if img_file.filename:
            img_filename = f"cover_{os.urandom(4).hex()}_{img_file.filename}"
            img_path = os.path.join(UPLOAD_DIR, img_filename)
            img_file.save(img_path)
            cover_image = img_filename

    if not full_text and request.form.get('full_text'):
        full_text = request.form.get('full_text', '')

    conn = get_db()
    cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    cur.execute('''
        INSERT INTO content (title, author, category, description, preview_text, cover_image, file_path, full_text, page_count, price, is_featured)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        RETURNING id
    ''', (title, author, category, description, preview_text, cover_image, file_path, full_text, page_count, price, is_featured))

    content_id = cur.fetchone()['id']
    conn.commit()

    cur.execute('SELECT * FROM content WHERE id = %s', (content_id,))
    new_item = cur.fetchone()
    cur.close()
    conn.close()

    return jsonify({'content': _serialize_content(new_item)}), 201

@content_bp.route('/api/content/<int:content_id>', methods=['PUT'])
@admin_required
def update_content(content_id):
    conn = get_db()
    cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    cur.execute('SELECT * FROM content WHERE id = %s', (content_id,))
    existing = cur.fetchone()

    if not existing:
        cur.close()
        conn.close()
        return jsonify({'error': 'Content not found'}), 404

    # Support both form-data and JSON
    if request.content_type and 'multipart/form-data' in request.content_type:
        title = request.form.get('title', existing['title'])
        author = request.form.get('author', existing['author'])
        category = request.form.get('category', existing['category'])
        description = request.form.get('description', existing['description'])
        preview_text = request.form.get('preview_text', existing['preview_text'])
        price = float(request.form.get('price', existing['price']))
        is_featured = request.form.get('is_featured', str(existing['is_featured'])) in ('1', 'true', 'True')
        full_text = request.form.get('full_text', existing['full_text'])
    else:
        data = request.get_json() or {}
        title = data.get('title', existing['title'])
        author = data.get('author', existing['author'])
        category = data.get('category', existing['category'])
        description = data.get('description', existing['description'])
        preview_text = data.get('preview_text', existing['preview_text'])
        price = float(data.get('price', existing['price']))
        is_featured = data.get('is_featured', existing['is_featured'])
        full_text = data.get('full_text', existing['full_text'])

    file_path = existing['file_path']
    page_count = existing['page_count']
    cover_image = existing['cover_image']

    # Handle new PDF upload
    if request.files and 'pdf_file' in request.files:
        pdf_file = request.files['pdf_file']
        if pdf_file.filename:
            filename = f"{title.replace(' ', '_').lower()}_{os.urandom(4).hex()}.pdf"
            filepath = os.path.join(UPLOAD_DIR, filename)
            pdf_file.save(filepath)
            file_path = filename

            try:
                reader = PdfReader(filepath)
                page_count = len(reader.pages)
                text_parts = []
                for page in reader.pages:
                    text = page.extract_text()
                    if text:
                        text_parts.append(text)
                full_text = '\n\n'.join(text_parts)
            except Exception as e:
                print(f"PDF extraction error: {e}")

    # Handle new cover image
    if request.files and 'cover_image' in request.files:
        img_file = request.files['cover_image']
        if img_file.filename:
            img_filename = f"cover_{os.urandom(4).hex()}_{img_file.filename}"
            img_path = os.path.join(UPLOAD_DIR, img_filename)
            img_file.save(img_path)
            cover_image = img_filename

    cur.execute('''
        UPDATE content SET title=%s, author=%s, category=%s, description=%s, preview_text=%s,
        cover_image=%s, file_path=%s, full_text=%s, page_count=%s, price=%s, is_featured=%s,
        updated_at=CURRENT_TIMESTAMP WHERE id=%s
    ''', (title, author, category, description, preview_text, cover_image, file_path,
          full_text, page_count, price, is_featured, content_id))

    conn.commit()
    cur.execute('SELECT * FROM content WHERE id = %s', (content_id,))
    updated = cur.fetchone()
    cur.close()
    conn.close()

    return jsonify({'content': _serialize_content(updated)})

@content_bp.route('/api/content/<int:content_id>', methods=['DELETE'])
@admin_required
def delete_content(content_id):
    conn = get_db()
    cur = conn.cursor()
    cur.execute('SELECT id FROM content WHERE id = %s', (content_id,))
    existing = cur.fetchone()

    if not existing:
        cur.close()
        conn.close()
        return jsonify({'error': 'Content not found'}), 404

    # Delete associated records
    cur.execute('DELETE FROM bookmarks WHERE content_id = %s', (content_id,))
    cur.execute('DELETE FROM reading_progress WHERE content_id = %s', (content_id,))
    cur.execute('DELETE FROM user_content_access WHERE content_id = %s', (content_id,))
    cur.execute('DELETE FROM payments WHERE content_id = %s', (content_id,))
    cur.execute('DELETE FROM content WHERE id = %s', (content_id,))
    conn.commit()
    cur.close()
    conn.close()

    return jsonify({'message': 'Content deleted successfully'})
