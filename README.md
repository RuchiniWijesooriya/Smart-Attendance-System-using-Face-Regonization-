# Smart Attendance System Using Face Recognition

## Project Overview
The Smart Attendance System Using Face Recognition is an AI-powered attendance management system that automatically marks attendance using face detection and recognition technology.

The system captures faces through a webcam, compares them with stored face encodings, and records attendance with date and time.

This project is suitable for:
- Schools
- Universities
- Training Institutes
- Offices

---

## Technologies Used

### Frontend
- HTML
- CSS
- JavaScript

### Backend
- Python
- Flask
- OpenCV
- face_recognition
- SQLite Database

---

## Project Structure

```text
smart-attendance/
│
├── frontend/
│   ├── index.html
│   ├── login.html
│   ├── dashboard.html
│   ├── students.html
│   ├── add-student.html
│   ├── face-capture.html
│   ├── live-attendance.html
│   ├── student-profile.html
│   ├── records.html
│   ├── reports.html
│   ├── notifications.html
│   ├── settings.html
│   ├── export.html
│   ├── admin-management.html
│   ├── styles.css
│   └── api.js
│
├── backend/
│   ├── app.py
│   ├── requirements.txt
│   ├── seed_data.py
│   │
│   ├── database/
│   │   └── db.py
│   │
│   ├── routes/
│   │   ├── auth_routes.py
│   │   ├── student_routes.py
│   │   ├── attendance_routes.py
│   │   ├── face_routes.py
│   │   └── report_routes.py
│   │
│   └── face_engine/
│       ├── detect.py
│       ├── encode.py
│       └── recognize.py
│
├── START_SERVER.bat
└── README.md
```

---

## Features

- Student Registration
- Face Capture & Enrollment
- Face Recognition
- Automatic Attendance Marking
- Attendance Records
- Dashboard Management
- CSV Export
- Admin Management

---

## Installation & Setup

### 1. Clone Repository

```bash
git clone https://github.com/your-username/smart-attendance.git
```

### 2. Navigate to Backend Folder

```bash
cd smart-attendance/backend
```

### 3. Install Required Libraries

```bash
pip install -r requirements.txt
```

### 4. Run Backend Server

```bash
python app.py
```

### 5. Open Frontend

Open:

```text
frontend/index.html
```

or use VS Code Live Server.

---

## System Workflow

1. Admin Login
2. Add Student Details
3. Capture Face Images
4. Generate Face Encoding
5. Start Live Attendance
6. Recognize Face
7. Mark Attendance Automatically
8. Store Data in Database
9. View Attendance Reports

---

## User Roles

### Admin
- Manage Students
- Capture Faces
- View Attendance
- Export Reports
- Manage Settings

### Student
- Automatic Face Recognition Attendance

---

## License

This project is developed for academic purposes only.

