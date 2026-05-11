"""
Database Initialization - SQLite
Creates all tables if they don't exist
"""

import sqlite3
import os


def get_db(db_path):
    """Get a database connection"""
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row  # Returns rows as dicts
    return conn


def init_db(db_path):
    """Initialize the database with all required tables"""
    os.makedirs(os.path.dirname(db_path), exist_ok=True)
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # ── Table: admin_users ─────────────────────────────────────────────
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS admin_users (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            name        TEXT    NOT NULL,
            email       TEXT    UNIQUE NOT NULL,
            password    TEXT    NOT NULL,
            role        TEXT    DEFAULT 'Teacher',  -- Super Admin / Admin / Teacher / Viewer
            status      TEXT    DEFAULT 'Active',
            created_at  TEXT    DEFAULT (datetime('now')),
            last_login  TEXT
        )
    ''')

    # ── Table: students ────────────────────────────────────────────────
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS students (
            id            INTEGER PRIMARY KEY AUTOINCREMENT,
            student_id    TEXT    UNIQUE NOT NULL,   -- e.g. STU001
            full_name     TEXT    NOT NULL,
            email         TEXT,
            phone         TEXT,
            gender        TEXT,
            dob           TEXT,
            department    TEXT,
            year          TEXT,
            class_group   TEXT,
            photo_path    TEXT,
            status        TEXT    DEFAULT 'Active',
            enrolled_date TEXT    DEFAULT (date('now')),
            created_at    TEXT    DEFAULT (datetime('now'))
        )
    ''')

    # ── Table: face_data ───────────────────────────────────────────────
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS face_data (
            id            INTEGER PRIMARY KEY AUTOINCREMENT,
            student_id    TEXT    NOT NULL,
            encoding_path TEXT    NOT NULL,   -- Path to stored face encoding (.npy file)
            sample_count  INTEGER DEFAULT 0,
            registered_at TEXT    DEFAULT (datetime('now')),
            FOREIGN KEY (student_id) REFERENCES students(student_id)
        )
    ''')

    # ── Table: attendance ──────────────────────────────────────────────
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS attendance (
            id            INTEGER PRIMARY KEY AUTOINCREMENT,
            student_id    TEXT    NOT NULL,
            subject       TEXT,
            date          TEXT    DEFAULT (date('now')),
            time_in       TEXT    DEFAULT (time('now')),
            status        TEXT    DEFAULT 'Present',  -- Present / Absent / Late
            confidence    REAL,
            method        TEXT    DEFAULT 'Face',     -- Face / Manual
            marked_by     TEXT,                       -- Admin user email
            created_at    TEXT    DEFAULT (datetime('now')),
            FOREIGN KEY (student_id) REFERENCES students(student_id)
        )
    ''')

    # ── Table: sessions ────────────────────────────────────────────────
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS sessions (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            subject     TEXT    NOT NULL,
            department  TEXT,
            teacher     TEXT,
            date        TEXT    DEFAULT (date('now')),
            start_time  TEXT,
            end_time    TEXT,
            status      TEXT    DEFAULT 'Active',    -- Active / Completed
            created_at  TEXT    DEFAULT (datetime('now'))
        )
    ''')

    # ── Table: notifications ───────────────────────────────────────────
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS notifications (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            type        TEXT,       -- alert / system
            title       TEXT,
            message     TEXT,
            is_read     INTEGER DEFAULT 0,
            created_at  TEXT    DEFAULT (datetime('now'))
        )
    ''')

    # ── Default Admin User (if not exists) ─────────────────────────────
    cursor.execute("SELECT COUNT(*) FROM admin_users WHERE email = 'admin@faceattend.com'")
    if cursor.fetchone()[0] == 0:
        cursor.execute('''
            INSERT INTO admin_users (name, email, password, role)
            VALUES (?, ?, ?, ?)
        ''', ('Admin User', 'admin@faceattend.com', 'admin123', 'Super Admin'))
        print("[DB] Default admin user created: admin@faceattend.com / admin123")

    conn.commit()
    conn.close()
    print(f"[DB] Database initialized: {db_path}")

