"""
Smart Attendance System - Main Flask Application
Tech Stack: Python + Flask + SQLite + OpenCV + face_recognition
"""

from flask import Flask, send_from_directory, jsonify
from flask_cors import CORS
import os

# ── Absolute paths ─────────────────────────────────────────────────────
BASE_DIR     = os.path.dirname(os.path.abspath(__file__))
# HTML/CSS/JS files are in the frontend folder (sibling to backend)
FRONTEND_DIR = os.path.abspath(os.path.join(BASE_DIR, '..', 'frontend'))
DB_PATH      = os.path.join(BASE_DIR, 'database', 'attendance.db')

# Import route blueprints
from routes.auth_routes       import auth_bp
from routes.student_routes    import student_bp
from routes.attendance_routes import attendance_bp
from routes.report_routes     import report_bp

# Face routes — only load if face_recognition is installed
try:
    from routes.face_routes import face_bp
    FACE_ENABLED = True
except ImportError:
    face_bp      = None
    FACE_ENABLED = False
    print("[WARNING] face_recognition not installed — face features disabled")

# Import DB initializer
from database.db import init_db

# ── App Setup ──────────────────────────────────────────────────────────
app = Flask(
    __name__,
    static_folder=FRONTEND_DIR,
    static_url_path=''
)

app.config['SECRET_KEY']    = 'faceattend-secret-2026'
app.config['SQLITEDB']      = DB_PATH
app.config['FACE_DATA_DIR'] = os.path.join(BASE_DIR, 'static', 'face_data')
app.config['UPLOAD_DIR']    = os.path.join(BASE_DIR, 'static', 'uploads')

CORS(app)

# ── Register Blueprints ────────────────────────────────────────────────
app.register_blueprint(auth_bp,       url_prefix='/api/auth')
app.register_blueprint(student_bp,    url_prefix='/api/students')
app.register_blueprint(attendance_bp, url_prefix='/api/attendance')
app.register_blueprint(report_bp,     url_prefix='/api/reports')

if FACE_ENABLED and face_bp:
    app.register_blueprint(face_bp, url_prefix='/api/face')

@app.route('/api/face/status-check')
def face_status_check():
    return jsonify({
        'enabled': FACE_ENABLED,
        'message': 'Face recognition ready' if FACE_ENABLED else
                   'Run: pip install opencv-python face-recognition numpy'
    })

# ── Frontend Page Routes ───────────────────────────────────────────────
@app.route('/')
def splash():
    return send_from_directory(FRONTEND_DIR, 'index.html')

@app.route('/login')
def login():
    return send_from_directory(FRONTEND_DIR, 'login.html')

@app.route('/dashboard')
def dashboard():
    return send_from_directory(FRONTEND_DIR, 'dashboard.html')

@app.route('/students')
def students():
    return send_from_directory(FRONTEND_DIR, 'students.html')

@app.route('/add-student')
def add_student():
    return send_from_directory(FRONTEND_DIR, 'add-student.html')

@app.route('/face-capture')
def face_capture():
    return send_from_directory(FRONTEND_DIR, 'face-capture.html')

@app.route('/live-attendance')
def live_attendance():
    return send_from_directory(FRONTEND_DIR, 'live-attendance.html')

@app.route('/student-profile')
def student_profile():
    return send_from_directory(FRONTEND_DIR, 'student-profile.html')

@app.route('/records')
def records():
    return send_from_directory(FRONTEND_DIR, 'records.html')

@app.route('/reports')
def reports():
    return send_from_directory(FRONTEND_DIR, 'reports.html')

@app.route('/notifications')
def notifications():
    return send_from_directory(FRONTEND_DIR, 'notifications.html')

@app.route('/settings')
def settings():
    return send_from_directory(FRONTEND_DIR, 'settings.html')

@app.route('/export')
def export():
    return send_from_directory(FRONTEND_DIR, 'export.html')

@app.route('/admin-management')
def admin_management():
    return send_from_directory(FRONTEND_DIR, 'admin-management.html')

# Catch-all: serve any static file (css, js, images)
@app.route('/<path:filename>')
def static_files(filename):
    return send_from_directory(FRONTEND_DIR, filename)

# ── Run App ────────────────────────────────────────────────────────────
if __name__ == '__main__':
    init_db(DB_PATH)
    print("=" * 50)
    print("  FaceAttend System Starting...")
    print(f"  Frontend: {FRONTEND_DIR}")
    print("  Open browser: http://localhost:5000")
    print("=" * 50)
    app.run(debug=True, host='0.0.0.0', port=5000)

