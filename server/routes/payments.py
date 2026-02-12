from flask import Blueprint, request, jsonify, g
import random
import string
import datetime
from database import get_db
from routes.auth import login_required

payments_bp = Blueprint('payments', __name__)

# In-memory OTP store (in production, use Redis or DB)
pending_otps = {}

def generate_otp():
    return ''.join(random.choices(string.digits, k=6))

def generate_transaction_id():
    return 'TXN' + ''.join(random.choices(string.ascii_uppercase + string.digits, k=12))

@payments_bp.route('/api/payments/initiate', methods=['POST'])
@login_required
def initiate_payment():
    data = request.get_json()
    content_id = data.get('content_id')
    phone_number = data.get('phone_number', '').strip()
    
    if not content_id or not phone_number:
        return jsonify({'error': 'Content ID and phone number are required'}), 400
    
    # Validate phone number format (Uganda)
    if not phone_number.startswith('+256') and not phone_number.startswith('0'):
        return jsonify({'error': 'Please enter a valid Ugandan phone number'}), 400
    
    db = get_db()
    
    # Check if user already has access
    access = db.execute(
        'SELECT id FROM user_content_access WHERE user_id = ? AND content_id = ?',
        (g.user_id, content_id)
    ).fetchone()
    
    if access:
        db.close()
        return jsonify({'error': 'You already have access to this content'}), 400
    
    # Get content price
    content = db.execute('SELECT id, title, price FROM content WHERE id = ?', (content_id,)).fetchone()
    if not content:
        db.close()
        return jsonify({'error': 'Content not found'}), 404
    
    # Generate OTP
    otp = generate_otp()
    txn_id = generate_transaction_id()
    
    # Create pending payment
    cursor = db.execute('''
        INSERT INTO payments (user_id, content_id, phone_number, amount, transaction_id, otp_code, status)
        VALUES (?, ?, ?, ?, ?, ?, 'pending')
    ''', (g.user_id, content_id, phone_number, content['price'], txn_id, otp))
    
    payment_id = cursor.lastrowid
    db.commit()
    db.close()
    
    # In a real app, this OTP would be sent via SMS
    # For simulation, we return it in the response
    return jsonify({
        'message': f'Payment initiated for "{content["title"]}". Enter the OTP to confirm.',
        'payment_id': payment_id,
        'transaction_id': txn_id,
        'amount': content['price'],
        'currency': 'UGX',
        'phone_number': phone_number,
        'otp_hint': f'Your simulated OTP is: {otp}'
    })

@payments_bp.route('/api/payments/confirm', methods=['POST'])
@login_required
def confirm_payment():
    data = request.get_json()
    payment_id = data.get('payment_id')
    otp = data.get('otp', '').strip()
    
    if not payment_id or not otp:
        return jsonify({'error': 'Payment ID and OTP are required'}), 400
    
    db = get_db()
    payment = db.execute(
        'SELECT * FROM payments WHERE id = ? AND user_id = ? AND status = ?',
        (payment_id, g.user_id, 'pending')
    ).fetchone()
    
    if not payment:
        db.close()
        return jsonify({'error': 'Payment not found or already processed'}), 404
    
    if payment['otp_code'] != otp:
        db.close()
        return jsonify({'error': 'Invalid OTP. Please try again.'}), 400
    
    # Confirm payment
    db.execute('UPDATE payments SET status = ? WHERE id = ?', ('confirmed', payment_id))
    
    # Grant content access
    db.execute('''
        INSERT OR IGNORE INTO user_content_access (user_id, content_id)
        VALUES (?, ?)
    ''', (g.user_id, payment['content_id']))
    
    db.commit()
    
    content = db.execute('SELECT title FROM content WHERE id = ?', (payment['content_id'],)).fetchone()
    db.close()
    
    return jsonify({
        'message': f'Payment confirmed! You now have access to "{content["title"]}".',
        'transaction_id': payment['transaction_id'],
        'content_id': payment['content_id']
    })

@payments_bp.route('/api/payments/history', methods=['GET'])
@login_required
def payment_history():
    db = get_db()
    payments = db.execute('''
        SELECT p.*, c.title as content_title 
        FROM payments p 
        LEFT JOIN content c ON p.content_id = c.id 
        WHERE p.user_id = ? 
        ORDER BY p.created_at DESC
    ''', (g.user_id,)).fetchall()
    db.close()
    
    return jsonify({'payments': [dict(p) for p in payments]})
