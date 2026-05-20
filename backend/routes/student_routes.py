"""
Student Routes
GET    /api/students         - Get all students
GET    /api/students/<id>    - Get single student
POST   /api/students         - Add new student
PUT    /api/students/<id>    - Update student
DELETE /api/students/<id>    - Delete student
"""

from flask import Blueprint, request, jsonify
from database.db import get_db
import os

student_bp = Blueprint('students', __name__)
DB_PATH = os.path.join(os.path.dirname(__file__), '..', 'database', 'attendance.db')


@student_bp.route('/', methods=['GET'])
def get_all_students():
    """Get all students with optional filters"""
    search = request.args.get('search', '')
    dept   = request.args.get('dept', '')
    status = request.args.get('status', '')

    query = 'SELECT * FROM students WHERE 1=1'
    params = []

    if search:
        query += ' AND (full_name LIKE ? OR student_id LIKE ?)'
        params += [f'%{search}%', f'%{search}%']
    if dept:
        query += ' AND department = ?'
        params.append(dept)
    if status:
        query += ' AND status = ?'
        params.append(status)

    query += ' ORDER BY created_at DESC'

    conn = get_db(DB_PATH)
    students = conn.execute(query, params).fetchall()

    # Check face registration for each student
    result = []
    for s in students:
        face = conn.execute(
            'SELECT sample_count FROM face_data WHERE student_id = ?',
            (s['student_id'],)
        ).fetchone()
        s_dict = dict(s)
        s_dict['face_registered'] = face is not None and face['sample_count'] >= 3
        result.append(s_dict)

    conn.close()
    return jsonify({'success': True, 'students': result, 'total': len(result)})


@student_bp.route('/<student_id>', methods=['GET'])
def get_student(student_id):
    """Get single student with attendance summary"""
    conn = get_db(DB_PATH)

    student = conn.execute(
        'SELECT * FROM students WHERE student_id = ?', (student_id,)
    ).fetchone()

    if not student:
        conn.close()
        return jsonify({'success': False, 'message': 'Student not found'}), 404

    # Attendance summary
    total = conn.execute(
        'SELECT COUNT(*) as cnt FROM attendance WHERE student_id = ?', (student_id,)
    ).fetchone()['cnt']

    present = conn.execute(
        'SELECT COUNT(*) as cnt FROM attendance WHERE student_id = ? AND status = "Present"', (student_id,)
    ).fetchone()['cnt']

    absent = conn.execute(
        'SELECT COUNT(*) as cnt FROM attendance WHERE student_id = ? AND status = "Absent"', (student_id,)
    ).fetchone()['cnt']

    late = conn.execute(
        'SELECT COUNT(*) as cnt FROM attendance WHERE student_id = ? AND status = "Late"', (student_id,)
    ).fetchone()['cnt']

    # Recent attendance history
    history = conn.execute(
        '''SELECT * FROM attendance WHERE student_id = ?
           ORDER BY date DESC, time_in DESC LIMIT 10''',
        (student_id,)
    ).fetchall()

    # Face data
    face = conn.execute(
        'SELECT * FROM face_data WHERE student_id = ?', (student_id,)
    ).fetchone()

    conn.close()

    att_pct = round((present / total * 100), 1) if total > 0 else 0

    return jsonify({
        'success': True,
        'student': dict(student),
        'attendance_summary': {
            'total': total, 'present': present,
            'absent': absent, 'late': late,
            'percentage': att_pct
        },
        'history': [dict(h) for h in history],
        'face_data': dict(face) if face else None
    })


@student_bp.route('/', methods=['POST'])
def add_student():
    """Add a new student"""
    data = request.get_json()

    required = ['student_id', 'full_name']
    for field in required:
        if not data.get(field):
            return jsonify({'success': False, 'message': f'{field} is required'}), 400

    conn = get_db(DB_PATH)

    # Check duplicate student_id
    existing = conn.execute(
        'SELECT id FROM students WHERE student_id = ?', (data['student_id'],)
    ).fetchone()

    if existing:
        conn.close()
        return jsonify({'success': False, 'message': 'Student ID already exists'}), 409

    conn.execute('''
        INSERT INTO students
            (student_id, full_name, email, phone, gender, dob,
             department, year, class_group, status)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (
        data['student_id'], data['full_name'],
        data.get('email', ''), data.get('phone', ''),
        data.get('gender', ''), data.get('dob', ''),
        data.get('department', ''), data.get('year', ''),
        data.get('class_group', ''), data.get('status', 'Active')
    ))
    conn.commit()
    conn.close()

    return jsonify({'success': True, 'message': 'Student added successfully'}), 201


@student_bp.route('/<student_id>', methods=['PUT'])
def update_student(student_id):
    """Update student info"""
    data = request.get_json()
    conn = get_db(DB_PATH)

    conn.execute('''
        UPDATE students SET
            full_name = ?, email = ?, phone = ?,
            gender = ?, dob = ?, department = ?,
            year = ?, class_group = ?, status = ?
        WHERE student_id = ?
    ''', (
        data.get('full_name'), data.get('email'), data.get('phone'),
        data.get('gender'), data.get('dob'), data.get('department'),
        data.get('year'), data.get('class_group'), data.get('status'),
        student_id
    ))
    conn.commit()
    conn.close()
    return jsonify({'success': True, 'message': 'Student updated'})


@student_bp.route('/<student_id>', methods=['DELETE'])
def delete_student(student_id):
    """Delete a student"""
    conn = get_db(DB_PATH)
    conn.execute('DELETE FROM students WHERE student_id = ?', (student_id,))
    conn.execute('DELETE FROM face_data WHERE student_id = ?', (student_id,))
    conn.execute('DELETE FROM attendance WHERE student_id = ?', (student_id,))
    conn.commit()
    conn.close()
    return jsonify({'success': True, 'message': 'Student deleted'})
