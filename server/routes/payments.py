from flask import Blueprint, request, jsonify, g
import random
import string
import datetime
from database import get_db
from routes.auth import login_required
import psycopg2.extras

payments_bp = Blueprint('payments', __name__)

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

    if not phone_number.startswith('+256') and not phone_number.startswith('0'):
        return jsonify({'error': 'Please enter a valid Ugandan phone number'}), 400

    conn = get_db()
    cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)

    # Check if user already has access
    cur.execute(
        'SELECT id FROM user_content_access WHERE user_id = %s AND content_id = %s',
        (g.user_id, content_id)
    )
    access = cur.fetchone()

    if access:
        cur.close()
        conn.close()
        return jsonify({'error': 'You already have access to this content'}), 400

    # Get content price
    cur.execute('SELECT id, title, price FROM content WHERE id = %s', (content_id,))
    content = cur.fetchone()
    if not content:
        cur.close()
        conn.close()
        return jsonify({'error': 'Content not found'}), 404

    # Generate OTP
    otp = generate_otp()
    txn_id = generate_transaction_id()

    # Create pending payment
    cur.execute('''
        INSERT INTO payments (user_id, content_id, phone_number, amount, transaction_id, otp_code, status)
        VALUES (%s, %s, %s, %s, %s, %s, 'pending')
        RETURNING id
    ''', (g.user_id, content_id, phone_number, content['price'], txn_id, otp))

    payment_id = cur.fetchone()['id']
    conn.commit()
    cur.close()
    conn.close()

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

    conn = get_db()
    cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    cur.execute(
        'SELECT * FROM payments WHERE id = %s AND user_id = %s AND status = %s',
        (payment_id, g.user_id, 'pending')
    )
    payment = cur.fetchone()

    if not payment:
        cur.close()
        conn.close()
        return jsonify({'error': 'Payment not found or already processed'}), 404

    if payment['otp_code'] != otp:
        cur.close()
        conn.close()
        return jsonify({'error': 'Invalid OTP. Please try again.'}), 400

    # Confirm payment
    cur.execute('UPDATE payments SET status = %s WHERE id = %s', ('confirmed', payment_id))

    # Grant content access
    cur.execute('''
        INSERT INTO user_content_access (user_id, content_id)
        VALUES (%s, %s)
        ON CONFLICT DO NOTHING
    ''', (g.user_id, payment['content_id']))

    conn.commit()

    cur.execute('SELECT title FROM content WHERE id = %s', (payment['content_id'],))
    content = cur.fetchone()
    cur.close()
    conn.close()

    return jsonify({
        'message': f'Payment confirmed! You now have access to "{content["title"]}".',
        'transaction_id': payment['transaction_id'],
        'content_id': payment['content_id']
    })

@payments_bp.route('/api/payments/history', methods=['GET'])
@login_required
def payment_history():
    conn = get_db()
    cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    cur.execute('''
        SELECT p.*, c.title as content_title
        FROM payments p
        LEFT JOIN content c ON p.content_id = c.id
        WHERE p.user_id = %s
        ORDER BY p.created_at DESC
    ''', (g.user_id,))
    payments = cur.fetchall()
    cur.close()
    conn.close()

    # Serialize datetimes
    for p in payments:
        if 'created_at' in p and p['created_at']:
            p['created_at'] = str(p['created_at'])

    return jsonify({'payments': [dict(p) for p in payments]})
