"""
Face Detection Module - Using OpenCV Haar Cascade
No external dependencies needed beyond opencv-python
"""
import cv2
import numpy as np

# Load Haar Cascade for face detection (comes with opencv-python)
CASCADE_PATH = cv2.data.haarcascades + 'haarcascade_frontalface_default.xml'
face_cascade = cv2.CascadeClassifier(CASCADE_PATH)


def detect_faces(frame):
    """
    Detect faces in a frame using OpenCV Haar Cascade.
    Returns list of (top, right, bottom, left) tuples.
    """
    if frame is None:
        return []

    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    faces = face_cascade.detectMultiScale(
        gray, scaleFactor=1.1, minNeighbors=5, minSize=(60, 60)
    )

    if len(faces) == 0:
        return []

    # Convert (x, y, w, h) to (top, right, bottom, left)
    locations = []
    for (x, y, w, h) in faces:
        locations.append((y, x + w, y + h, x))
    return locations
