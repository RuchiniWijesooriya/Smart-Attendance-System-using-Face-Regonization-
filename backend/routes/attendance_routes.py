"""
Attendance Routes
GET  /api/attendance/records   - Get all records (with filters)
POST /api/attendance/mark      - Mark attendance manually
GET  /api/attendance/summary   - Dashboard summary stats
POST /api/attendance/session   - Start/stop attendance session
"""

from flask import Blueprint, request, jsonify
from database.db import get_db
from datetime import date, datetime
import os

attendance_bp = Blueprint('attendance', __name__)
DB_PATH = os.path.join(os.path.dirname(__file__), '..', 'database', 'attendance.db')


@attendance_bp.route('/records', methods=['GET'])
def get_records():
    """Get attendance records with filters"""
    search      = request.args.get('search', '')
    status      = request.args.get('status', '')
    subject     = request.args.get('subject', '')
    date_from   = request.args.get('date_from', '')
    date_to     = request.args.get('date_to', '')

    query = '''
        SELECT a.*, s.full_name, s.department
        FROM attendance a
        JOIN students s ON a.student_id = s.student_id
        WHERE 1=1
    '''
    params = []

    if search:
        query += ' AND (s.full_name LIKE ? OR a.student_id LIKE ?)'
        params += [f'%{search}%', f'%{search}%']
    if status:
        query += ' AND a.status = ?'
        params.append(status)
    if subject:
        query += ' AND a.subject = ?'
        params.append(subject)
    if date_from:
        query += ' AND a.date >= ?'
        params.append(date_from)
    if date_to:
        query += ' AND a.date <= ?'
        params.append(date_to)

    query += ' ORDER BY a.date DESC, a.time_in DESC'

    conn = get_db(DB_PATH)
    records = conn.execute(query, params).fetchall()
    conn.close()

    return jsonify({
        'success': True,
        'records': [dict(r) for r in records],
        'total': len(records)
    })


@attendance_bp.route('/summary', methods=['GET'])
def get_summary():
    """Dashboard summary stats for today"""
    today = date.today().isoformat()
    conn = get_db(DB_PATH)

    total_students = conn.execute('SELECT COUNT(*) FROM students WHERE status="Active"').fetchone()[0]
    present_today  = conn.execute(
        'SELECT COUNT(DISTINCT student_id) FROM attendance WHERE date=? AND status="Present"',
        (today,)
    ).fetchone()[0]
    absent_today   = conn.execute(
        'SELECT COUNT(DISTINCT student_id) FROM attendance WHERE date=? AND status="Absent"',
        (today,)
    ).fetchone()[0]
    late_today     = conn.execute(
        'SELECT COUNT(DISTINCT student_id) FROM attendance WHERE date=? AND status="Late"',
        (today,)
    ).fetchone()[0]

    # Recent activity (last 10)
    recent = conn.execute('''
        SELECT a.*, s.full_name FROM attendance a
        JOIN students s ON a.student_id = s.student_id
        ORDER BY a.created_at DESC LIMIT 10
    ''').fetchall()

    conn.close()

    return jsonify({
        'success': True,
        'summary': {
            'total_students': total_students,
            'present_today':  present_today,
            'absent_today':   absent_today,
            'late_today':     late_today,
            'date': today
        },
        'recent_activity': [dict(r) for r in recent]
    })


@attendance_bp.route('/mark', methods=['POST'])
def mark_attendance():
    """Manually mark attendance for a student"""
    data = request.get_json()

    student_id = data.get('student_id')
    status     = data.get('status', 'Present')
    subject    = data.get('subject', '')
    method     = data.get('method', 'Manual')

    if not student_id:
        return jsonify({'success': False, 'message': 'student_id required'}), 400

    conn = get_db(DB_PATH)

    # Check if already marked today
    existing = conn.execute(
        'SELECT id FROM attendance WHERE student_id=? AND date=date("now") AND subject=?',
        (student_id, subject)
    ).fetchone()

    if existing:
        # Update existing record
        conn.execute(
            'UPDATE attendance SET status=?, method=? WHERE id=?',
            (status, method, existing['id'])
        )
    else:
        # Insert new record
        conn.execute('''
            INSERT INTO attendance (student_id, subject, status, method, confidence)
            VALUES (?, ?, ?, ?, ?)
        ''', (student_id, subject, status, method, data.get('confidence')))

    conn.commit()
    conn.close()

    return jsonify({'success': True, 'message': f'Attendance marked: {status}'})


@attendance_bp.route('/session', methods=['POST'])
def manage_session():
    """Start or stop an attendance session"""
    data   = request.get_json()
    action = data.get('action', 'start')  # start / stop

    conn = get_db(DB_PATH)

    if action == 'start':
        cursor = conn.execute('''
            INSERT INTO sessions (subject, department, teacher, start_time, status)
            VALUES (?, ?, ?, time('now'), 'Active')
        ''', (data.get('subject'), data.get('department'), data.get('teacher')))
        session_id = cursor.lastrowid
        conn.commit()
        conn.close()
        return jsonify({'success': True, 'session_id': session_id, 'message': 'Session started'})

    elif action == 'stop':
        session_id = data.get('session_id')
        conn.execute(
            'UPDATE sessions SET end_time=time("now"), status="Completed" WHERE id=?',
            (session_id,)
        )
        conn.commit()
        conn.close()
        return jsonify({'success': True, 'message': 'Session ended'})

    conn.close()
    return jsonify({'success': False, 'message': 'Invalid action'}), 400


@attendance_bp.route('/weekly', methods=['GET'])
def weekly_stats():
    """Get weekly attendance stats for chart"""
    conn = get_db(DB_PATH)
    rows = conn.execute('''
        SELECT date,
               SUM(CASE WHEN status="Present" THEN 1 ELSE 0 END) as present,
               SUM(CASE WHEN status="Absent"  THEN 1 ELSE 0 END) as absent,
               SUM(CASE WHEN status="Late"    THEN 1 ELSE 0 END) as late
        FROM attendance
        WHERE date >= date('now', '-7 days')
        GROUP BY date ORDER BY date
    ''').fetchall()
    conn.close()
    return jsonify({'success': True, 'data': [dict(r) for r in rows]})
