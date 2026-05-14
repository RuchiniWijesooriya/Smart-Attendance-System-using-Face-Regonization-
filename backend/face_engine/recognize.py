"""
Face Recognition Module - Using OpenCV (no dlib needed!)
Compares face encodings using cosine similarity.
"""
import numpy as np


def recognize_face(frame, face_location, known_encodings, known_ids, threshold=0.6):
    """
    Compare detected face against all known encodings using cosine similarity.

    Args:
        frame             : BGR image (numpy array)
        face_location     : (top, right, bottom, left) tuple
        known_encodings   : List of known face encoding arrays
        known_ids         : List of student_ids matching known_encodings
        threshold         : Similarity threshold (higher = stricter, 0.0-1.0)

    Returns:
        (student_id, confidence) or (None, confidence)
    """
    if not known_encodings:
        return None, 0.0

    import cv2
    from face_engine.encode import encode_face

    # Get encoding for the detected face
    face_enc = encode_face(frame, face_location)
    if face_enc is None:
        return None, 0.0

    # Calculate cosine similarity with all known faces
    best_id   = None
    best_sim  = -1.0

    for i, known_enc in enumerate(known_encodings):
        # Cosine similarity
        dot      = np.dot(face_enc, known_enc)
        norm_a   = np.linalg.norm(face_enc)
        norm_b   = np.linalg.norm(known_enc)

        if norm_a == 0 or norm_b == 0:
            continue

        similarity = dot / (norm_a * norm_b)

        if similarity > best_sim:
            best_sim = similarity
            best_id  = known_ids[i]

    confidence = max(0.0, best_sim)

    if confidence >= threshold:
        return best_id, confidence

    return None, confidence

