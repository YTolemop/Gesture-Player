from pathlib import Path
import numpy as np
import cv2
import mediapipe as mp
from mediapipe.tasks import python
from mediapipe.tasks.python import vision
from core.types import RawHandSample

MODEL = Path(__file__).resolve().parents[1] / 'assets/models/hand_landmarker.task'

class Landmarks:
    def __init__(self, swap_handedness=False):
        self.swap_handedness=swap_handedness
        if not MODEL.is_file():
            raise RuntimeError('缺少關鍵點模型，請執行 python main.py prepare')
        from core.resources import verify_model
        verify_model()
        # Native Windows file APIs in MediaPipe may fail on non-ASCII paths.
        # Loading verified bytes also keeps the model strictly local/offline.
        self.detector = vision.HandLandmarker.create_from_options(vision.HandLandmarkerOptions(base_options=python.BaseOptions(model_asset_buffer=MODEL.read_bytes()), running_mode=vision.RunningMode.VIDEO, num_hands=2))
        self.last_ms = -1

    def detect(self, frame, timestamp, camera):
        self.last_ms = max(self.last_ms + 1, int(timestamp * 1000))
        result = self.detector.detect_for_video(mp.Image(image_format=mp.ImageFormat.SRGB, data=cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)), self.last_ms)
        slots = {'Left': None, 'Right': None}
        ambiguous = set()
        for points, handedness in zip(result.hand_landmarks, result.handedness):
            if not handedness:
                continue
            cat = handedness[0]
            name=cat.category_name
            if self.swap_handedness and name in slots:name='Right' if name=='Left' else 'Left'
            if name not in slots or cat.score < .7 or name in ambiguous:
                continue
            if slots[name] is not None:
                slots[name] = None
                ambiguous.add(name)
                continue
            slots[name] = np.array([[p.x, p.y, p.z] for p in points], dtype=np.float32)
        return RawHandSample(slots['Left'], slots['Right'], frame.shape[1], frame.shape[0], timestamp, camera=camera)

    def close(self):
        self.detector.close()
