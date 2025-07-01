import insightface
import numpy as np
import cv2

class FaceModel:
    def __init__(self):
        self.model = insightface.app.FaceAnalysis(name='buffalo_l')
        self.model.prepare(ctx_id=0, det_size=(640, 640))

    def get_face_embedding(self, image: np.ndarray):
        faces = self.model.get(image)
        if len(faces) == 0:
            return None, 'No face detected.'
        if len(faces) > 1:
            return None, 'Multiple faces detected.'
        return faces[0].embedding, None

    def detect_faces(self, image: np.ndarray):
        return self.model.get(image) 