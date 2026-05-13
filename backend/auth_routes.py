"""
Authentication Routes
POST /api/auth/login
POST /api/auth/logout
GET  /api/auth/me
"""

from flask import Blueprint, request, jsonify, session
from database.db import get_db
import os

auth_bp = Blueprint('auth', __name__)
DB_PATH = os.path.join(os.path.dirname(__file__), '..', 'database', 'attendance.db')


@auth_bp.route('/login', methods=['POST'])
def login():
    """Login - Admin / Teacher / Viewer"""
    data = request.get_json()
    email    = data.get('email', '').strip()
    password = data.get('password', '').strip()

    if not email or not password:
        return jsonify({'success': False, 'message': 'Email and password required'}), 400

    conn = get_db(DB_PATH)
    user = conn.execute(
        'SELECT * FROM admin_users WHERE email = ? AND password = ? AND status = "Active"',
        (email, password)
    ).fetchone()
    conn.close()

    if not user:
        return jsonify({'success': False, 'message': 'Invalid credentials'}), 401

    # Update last login
    conn = get_db(DB_PATH)
    conn.execute("UPDATE admin_users SET last_login = datetime('now') WHERE email = ?", (email,))
    conn.commit()
    conn.close()

    return jsonify({
        'success': True,
        'message': 'Login successful',
        'user': {
            'id':    user['id'],
            'name':  user['name'],
            'email': user['email'],
            'role':  user['role']
        }
    })


@auth_bp.route('/logout', methods=['POST'])
def logout():
    return jsonify({'success': True, 'message': 'Logged out'})


@auth_bp.route('/me', methods=['GET'])
def me():
    """Get current user info (demo - returns default admin)"""
    return jsonify({
        'success': True,
        'user': {'name': 'Admin User', 'email': 'admin@faceattend.com', 'role': 'Super Admin'}
    })
