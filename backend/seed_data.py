"""
Seed script - adds sample data to the database for testing
Run once: python seed_data.py
"""
import sys, os
sys.path.insert(0, os.path.dirname(__file__))

from database.db import init_db, get_db

DB_PATH = os.path.join(os.path.dirname(__file__), 'database', 'attendance.db')

# Initialize DB first
init_db(DB_PATH)

conn = get_db(DB_PATH)

# ── Admin Users ───────────────────────────────────────────────────────
admins = [
    ('Dr. Nimal Perera',    'nimal@university.edu',    'teacher123', 'Teacher'),
    ('Dr. Sujatha Fernando','sujatha@university.edu',  'teacher123', 'Teacher'),
    ('Mr. Viewer User',     'viewer@university.edu',   'viewer123',  'Viewer'),
]
for name, email, pwd, role in admins:
    existing = conn.execute('SELECT id FROM admin_users WHERE email=?', (email,)).fetchone()
    if not existing:
        conn.execute(
            'INSERT INTO admin_users (name, email, password, role) VALUES (?,?,?,?)',
            (name, email, pwd, role)
        )

# ── Students ──────────────────────────────────────────────────────────
students = [
    ('STU001','Kavindu Perera',   'kavindu@cs.edu',  '+94771234567','Male',  '2003-05-12','Computer Science','Year 3','CS301'),
    ('STU002','Sameera Silva',    'sameera@cs.edu',  '+94772345678','Male',  '2003-08-20','Computer Science','Year 3','CS301'),
    ('STU003','Ruchini Fernando', 'ruchini@eng.edu', '+94773456789','Female','2003-02-15','Engineering',     'Year 3','ENG301'),
    ('STU004','Tharushi Mendis',  'tharushi@biz.edu','+94774567890','Female','2003-11-08','Business',        'Year 3','BIZ301'),
    ('STU005','Dinesh Rathnayake','dinesh@cs.edu',   '+94775678901','Male',  '2002-07-25','Computer Science','Year 3','CS301'),
    ('STU006','Ashini Jayawardena','ashini@eng.edu', '+94776789012','Female','2003-03-30','Engineering',     'Year 3','ENG301'),
    ('STU007','Savindu Kumara',   'savindu@cs.edu',  '+94777890123','Male',  '2003-09-14','Computer Science','Year 3','CS302'),
    ('STU008','Nimal Bandara',    'nimal.s@biz.edu', '+94778901234','Male',  '2002-12-05','Business',        'Year 3','BIZ301'),
    ('STU009','Chamari Perera',   'chamari@eng.edu', '+94779012345','Female','2003-06-18','Engineering',     'Year 3','ENG302'),
    ('STU010','Lasith Malinga',   'lasith@cs.edu',   '+94770123456','Male',  '2003-01-22','Computer Science','Year 3','CS302'),
]
for s in students:
    existing = conn.execute('SELECT id FROM students WHERE student_id=?', (s[0],)).fetchone()
    if not existing:
        conn.execute('''
            INSERT INTO students
                (student_id,full_name,email,phone,gender,dob,department,year,class_group)
            VALUES (?,?,?,?,?,?,?,?,?)
        ''', s)

# ── Sample Attendance Records ─────────────────────────────────────────
records = [
    # (student_id, subject, date, time_in, status, confidence, method)
    ('STU001','CS301','2026-04-27','08:42','Present',96.0,'Face'),
    ('STU002','CS301','2026-04-27','08:44','Present',93.0,'Face'),
    ('STU003','CS301','2026-04-27','09:05','Late',   89.0,'Face'),
    ('STU004','CS301','2026-04-27','',     'Absent', None, 'Auto'),
    ('STU005','CS302','2026-04-27','09:01','Present',95.0,'Face'),
    ('STU006','CS302','2026-04-27','09:03','Present',97.0,'Face'),
    ('STU007','CS302','2026-04-27','09:12','Late',   88.0,'Face'),
    ('STU008','BIZ301','2026-04-26','',    'Absent', None, 'Auto'),
    ('STU009','ENG301','2026-04-26','08:38','Present',98.0,'Face'),
    ('STU010','CS303','2026-04-26','Manual','Present',None,'Manual'),
    ('STU001','CS302','2026-04-25','08:40','Present',94.0,'Face'),
    ('STU002','CS303','2026-04-25','08:36','Present',92.0,'Face'),
    ('STU005','CS301','2026-04-25','',     'Absent', None,'Auto'),
    ('STU006','CS301','2026-04-24','08:41','Present',96.0,'Face'),
    ('STU003','CS302','2026-04-24','09:10','Late',   87.0,'Face'),
    ('STU001','CS303','2026-04-24','08:35','Present',95.0,'Face'),
    ('STU004','CS302','2026-04-23','',     'Absent', None,'Auto'),
    ('STU008','CS301','2026-04-23','',     'Absent', None,'Auto'),
    ('STU009','CS302','2026-04-22','08:39','Present',91.0,'Face'),
    ('STU010','ENG301','2026-04-22','08:50','Late',  85.0,'Face'),
]
for r in records:
    existing = conn.execute(
        'SELECT id FROM attendance WHERE student_id=? AND date=? AND subject=?',
        (r[0], r[2], r[1])
    ).fetchone()
    if not existing:
        conn.execute('''
            INSERT INTO attendance
                (student_id,subject,date,time_in,status,confidence,method)
            VALUES (?,?,?,?,?,?,?)
        ''', r)

# ── Sample Notifications ──────────────────────────────────────────────
notifs = [
    ('alert', 'Low Attendance Alert',    'Nimal Bandara (STU008) attendance dropped to 45%'),
    ('alert', '3 Day Absence',           'Tharushi Mendis (STU004) absent 3 consecutive days'),
    ('system','Unknown Face Detected',   'Unrecognized face during CS301 session at 09:45 AM'),
    ('system','Report Generated',        'Monthly attendance report for April 2026 generated'),
    ('system','New Student Enrolled',    'Chamari Perera (STU009) enrolled successfully'),
]
for n in notifs:
    conn.execute(
        'INSERT INTO notifications (type,title,message) VALUES (?,?,?)', n
    )

conn.commit()
conn.close()
print("=" * 50)
print("  Seed data inserted successfully!")
print("  Students: 10")
print("  Attendance records: 20")
print("  Admin users: 3 + 1 default")
print("=" * 50)
