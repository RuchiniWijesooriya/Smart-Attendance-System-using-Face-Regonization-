"""
Face Encoding Module - Using OpenCV (no dlib/face_recognition needed!)
Uses LBPH (Local Binary Pattern Histograms) for face encoding.
"""
import cv2
import numpy as np


def encode_face(frame, face_location):
    """
    Extract face region and return it as a normalized encoding.
    Uses pixel data of face region resized to 100x100 as encoding.

    Args:
        frame         : BGR image (numpy array)
        face_location : (top, right, bottom, left) tuple

    Returns:
        encoding (flattened numpy array) or None
    """
    if frame is None:
        return None

    top, right, bottom, left = face_location

    face_region = frame[top:bottom, left:right]

    if face_region.size == 0:
        return None

    gray_face = cv2.cvtColor(face_region, cv2.COLOR_BGR2GRAY)
    resized   = cv2.resize(gray_face, (100, 100))

    encoding = resized.astype(np.float64).flatten() / 255.0
    return encoding