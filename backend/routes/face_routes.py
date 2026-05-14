"""
Face Recognition Routes — Pure OpenCV (no dlib needed!)
POST /api/face/enroll     - Register student face
POST /api/face/recognize  - Recognize face from frame
GET  /api/face/status/<id>- Check face registration status
DELETE /api/face/<id>     - Remove face data
"""

from flask import Blueprint, request, jsonify
from database.db import get_db
from face_engine.detect import detect_faces
from face_engine.encode import encode_face
from face_engine.recognize import recognize_face
import os, base64, cv2
import numpy as np

face_bp = Blueprint('face', __name__)
DB_PATH  = os.path.join(os.path.dirname(__file__), '..', 'database', 'attendance.db')
FACE_DIR = os.path.join(os.path.dirname(__file__), '..', 'static', 'face_data')


def decode_base64_image(img_b64):
    """Decode a base64 image string to OpenCV frame"""
    img_bytes = base64.b64decode(img_b64.split(',')[-1])
    img_array = np.frombuffer(img_bytes, dtype=np.uint8)
    frame     = cv2.imdecode(img_array, cv2.IMREAD_COLOR)
    return frame


@face_bp.route('/enroll', methods=['POST'])
def enroll_face():
    """Enroll student face from base64 image"""
    data       = request.get_json()
    student_id = data.get('student_id')
    img_b64    = data.get('image_base64')

    if not student_id or not img_b64:
        return jsonify({'success': False, 'message': 'student_id and image_base64 required'}), 400

    try:
        frame = decode_base64_image(img_b64)
    except Exception as e:
        return jsonify({'success': False, 'message': f'Image decode error: {str(e)}'}), 400

    # Detect face
    faces = detect_faces(frame)
    if not faces:
        return jsonify({'success': False, 'message': 'No face detected in image'}), 400

    # Encode face
    encoding = encode_face(frame, faces[0])
    if encoding is None:
        return jsonify({'success': False, 'message': 'Could not encode face'}), 400

    # Save encoding
    os.makedirs(FACE_DIR, exist_ok=True)
    conn = get_db(DB_PATH)

    existing = conn.execute(
        'SELECT id, sample_count, encoding_path FROM face_data WHERE student_id=?',
        (student_id,)
    ).fetchone()

    if existing:
        enc_path  = existing['encoding_path']
        old_encs  = np.load(enc_path, allow_pickle=True).tolist()
        old_encs.append(encoding)
        np.save(enc_path, np.array(old_encs))
        sample_count = existing['sample_count'] + 1
        conn.execute('UPDATE face_data SET sample_count=? WHERE student_id=?',
                     (sample_count, student_id))
    else:
        enc_path     = os.path.join(FACE_DIR, f'{student_id}.npy')
        np.save(enc_path, np.array([encoding]))
        sample_count = 1
        conn.execute(
            'INSERT INTO face_data (student_id, encoding_path, sample_count) VALUES (?,?,?)',
            (student_id, enc_path, sample_count))

    conn.commit()
    conn.close()

    return jsonify({
        'success':      True,
        'message':      f'Face sample {sample_count}/3 saved',
        'sample_count': sample_count,
        'enrolled':     sample_count >= 3
    })


@face_bp.route('/recognize', methods=['POST'])
def recognize():
    """Recognize face from camera frame"""
    data    = request.get_json()
    img_b64 = data.get('image_base64')
    subject = data.get('subject', '')

    if not img_b64:
        return jsonify({'success': False, 'message': 'image_base64 required'}), 400

    try:
        frame = decode_base64_image(img_b64)
    except Exception as e:
        return jsonify({'success': False, 'message': f'Decode error: {str(e)}'}), 400

    faces = detect_faces(frame)
    if not faces:
        return jsonify({'success': True, 'recognized': [], 'message': 'No faces detected'})

    conn = get_db(DB_PATH)

    # Load all registered encodings
    all_face_data    = conn.execute(
        'SELECT student_id, encoding_path FROM face_data WHERE sample_count >= 3'
    ).fetchall()

    known_encodings = []
    known_ids       = []
    for fd in all_face_data:
        if os.path.exists(fd['encoding_path']):
            encs = np.load(fd['encoding_path'], allow_pickle=True)
            known_encodings.append(np.mean(encs, axis=0))
            known_ids.append(fd['student_id'])

    results = []
    for face_loc in faces:
        student_id, confidence = recognize_face(
            frame, face_loc, known_encodings, known_ids
        )

        if student_id:
            student = conn.execute(
                'SELECT student_id, full_name, department FROM students WHERE student_id=?',
                (student_id,)
            ).fetchone()

            if student:
                existing = conn.execute(
                    'SELECT id FROM attendance WHERE student_id=? AND date=date("now") AND subject=?',
                    (student_id, subject)
                ).fetchone()

                if not existing:
                    conn.execute('''
                        INSERT INTO attendance (student_id, subject, status, method, confidence)
                        VALUES (?, ?, "Present", "Face", ?)
                    ''', (student_id, subject, confidence))
                    conn.commit()

                results.append({
                    'student_id':    student['student_id'],
                    'full_name':     student['full_name'],
                    'department':    student['department'],
                    'confidence':    round(confidence * 100, 1),
                    'status':        'Present',
                    'face_location': list(face_loc)
                })
        else:
            results.append({
                'student_id': None,
                'full_name':  'Unknown',
                'confidence': round(confidence * 100, 1) if confidence else 0,
                'status':     'Unknown',
                'face_location': list(face_loc)
            })

    conn.close()
    return jsonify({'success': True, 'recognized': results})


@face_bp.route('/status/<student_id>', methods=['GET'])
def face_status(student_id):
    """Check face registration status"""
    conn = get_db(DB_PATH)
    face = conn.execute(
        'SELECT * FROM face_data WHERE student_id=?', (student_id,)
    ).fetchone()
    conn.close()

    if face:
        return jsonify({
            'success':       True,
            'registered':    face['sample_count'] >= 3,
            'sample_count':  face['sample_count'],
            'registered_at': face['registered_at']
        })
    return jsonify({'success': True, 'registered': False, 'sample_count': 0})


@face_bp.route('/<student_id>', methods=['DELETE'])
def delete_face(student_id):
    """Remove face data for a student"""
    conn = get_db(DB_PATH)
    face = conn.execute(
        'SELECT encoding_path FROM face_data WHERE student_id=?', (student_id,)
    ).fetchone()

    if face and os.path.exists(face['encoding_path']):
        os.remove(face['encoding_path'])

    conn.execute('DELETE FROM face_data WHERE student_id=?', (student_id,))
    conn.commit()
    conn.close()
    return jsonify({'success': True, 'message': 'Face data removed'})

