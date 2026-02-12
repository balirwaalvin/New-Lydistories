from flask import Blueprint, request, jsonify, g
import os
from database import get_db
from routes.auth import login_required, admin_required, optional_auth
from PyPDF2 import PdfReader

content_bp = Blueprint('content', __name__)

UPLOAD_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'server', 'uploads')
if not os.path.exists(UPLOAD_DIR):
    os.makedirs(UPLOAD_DIR, exist_ok=True)

# Recalculate relative to server dir
UPLOAD_DIR = os.path.join(os.path.dirname(__file__), '..', 'uploads')
UPLOAD_DIR = os.path.abspath(UPLOAD_DIR)
os.makedirs(UPLOAD_DIR, exist_ok=True)

@content_bp.route('/api/content', methods=['GET'])
@optional_auth
def list_content():
    category = request.args.get('category', '')
    search = request.args.get('search', '')
    featured = request.args.get('featured', '')
    
    db = get_db()
    query = 'SELECT id, title, author, category, description, preview_text, cover_image, page_count, price, is_featured, created_at FROM content WHERE 1=1'
    params = []
    
    if category:
        query += ' AND category = ?'
        params.append(category)
    if search:
        query += ' AND (title LIKE ? OR author LIKE ? OR description LIKE ?)'
        params.extend([f'%{search}%'] * 3)
    if featured:
        query += ' AND is_featured = 1'
    
    query += ' ORDER BY created_at DESC'
    
    rows = db.execute(query, params).fetchall()
    content_list = [dict(row) for row in rows]
    
    # Check user access for each content item
    if g.user_id:
        for item in content_list:
            access = db.execute(
                'SELECT id FROM user_content_access WHERE user_id = ? AND content_id = ?',
                (g.user_id, item['id'])
            ).fetchone()
            item['has_access'] = access is not None
            # Admin always has access
            if g.user_role == 'admin':
                item['has_access'] = True
    else:
        for item in content_list:
            item['has_access'] = False
    
    db.close()
    return jsonify({'content': content_list})

@content_bp.route('/api/content/<int:content_id>', methods=['GET'])
@optional_auth
def get_content(content_id):
    db = get_db()
    item = db.execute('SELECT * FROM content WHERE id = ?', (content_id,)).fetchone()
    
    if not item:
        db.close()
        return jsonify({'error': 'Content not found'}), 404
    
    result = dict(item)
    has_access = False
    
    if g.user_id:
        access = db.execute(
            'SELECT id FROM user_content_access WHERE user_id = ? AND content_id = ?',
            (g.user_id, content_id)
        ).fetchone()
        has_access = access is not None
        if g.user_role == 'admin':
            has_access = True
    
    result['has_access'] = has_access
    
    if not has_access:
        # Only return preview for non-paid users
        result.pop('full_text', None)
        result.pop('file_path', None)
    
    db.close()
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
    is_featured = int(request.form.get('is_featured', 0))
    
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
            
            # Extract text from PDF
            try:
                reader = PdfReader(filepath)
                page_count = len(reader.pages)
                text_parts = []
                for page in reader.pages:
                    text = page.extract_text()
                    if text:
                        text_parts.append(text)
                full_text = '\n\n'.join(text_parts)
                
                # Auto-generate preview if not provided
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
    
    # If full_text provided directly (for non-PDF content)
    if not full_text and request.form.get('full_text'):
        full_text = request.form.get('full_text', '')
    
    db = get_db()
    cursor = db.execute('''
        INSERT INTO content (title, author, category, description, preview_text, cover_image, file_path, full_text, page_count, price, is_featured)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (title, author, category, description, preview_text, cover_image, file_path, full_text, page_count, price, is_featured))
    
    content_id = cursor.lastrowid
    db.commit()
    
    new_item = db.execute('SELECT * FROM content WHERE id = ?', (content_id,)).fetchone()
    db.close()
    
    return jsonify({'content': dict(new_item)}), 201

@content_bp.route('/api/content/<int:content_id>', methods=['PUT'])
@admin_required
def update_content(content_id):
    db = get_db()
    existing = db.execute('SELECT * FROM content WHERE id = ?', (content_id,)).fetchone()
    
    if not existing:
        db.close()
        return jsonify({'error': 'Content not found'}), 404
    
    # Support both form-data and JSON
    if request.content_type and 'multipart/form-data' in request.content_type:
        title = request.form.get('title', existing['title'])
        author = request.form.get('author', existing['author'])
        category = request.form.get('category', existing['category'])
        description = request.form.get('description', existing['description'])
        preview_text = request.form.get('preview_text', existing['preview_text'])
        price = float(request.form.get('price', existing['price']))
        is_featured = int(request.form.get('is_featured', existing['is_featured']))
        full_text = request.form.get('full_text', existing['full_text'])
    else:
        data = request.get_json() or {}
        title = data.get('title', existing['title'])
        author = data.get('author', existing['author'])
        category = data.get('category', existing['category'])
        description = data.get('description', existing['description'])
        preview_text = data.get('preview_text', existing['preview_text'])
        price = float(data.get('price', existing['price']))
        is_featured = int(data.get('is_featured', existing['is_featured']))
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
    
    db.execute('''
        UPDATE content SET title=?, author=?, category=?, description=?, preview_text=?,
        cover_image=?, file_path=?, full_text=?, page_count=?, price=?, is_featured=?,
        updated_at=CURRENT_TIMESTAMP WHERE id=?
    ''', (title, author, category, description, preview_text, cover_image, file_path,
          full_text, page_count, price, is_featured, content_id))
    
    db.commit()
    updated = db.execute('SELECT * FROM content WHERE id = ?', (content_id,)).fetchone()
    db.close()
    
    return jsonify({'content': dict(updated)})

@content_bp.route('/api/content/<int:content_id>', methods=['DELETE'])
@admin_required
def delete_content(content_id):
    db = get_db()
    existing = db.execute('SELECT * FROM content WHERE id = ?', (content_id,)).fetchone()
    
    if not existing:
        db.close()
        return jsonify({'error': 'Content not found'}), 404
    
    # Delete associated records
    db.execute('DELETE FROM bookmarks WHERE content_id = ?', (content_id,))
    db.execute('DELETE FROM reading_progress WHERE content_id = ?', (content_id,))
    db.execute('DELETE FROM user_content_access WHERE content_id = ?', (content_id,))
    db.execute('DELETE FROM payments WHERE content_id = ?', (content_id,))
    db.execute('DELETE FROM content WHERE id = ?', (content_id,))
    db.commit()
    db.close()
    
    return jsonify({'message': 'Content deleted successfully'})
