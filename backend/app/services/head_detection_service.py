from __future__ import annotations

import random

import cv2

try:
    from ultralytics import YOLO
except Exception:  # pragma: no cover - optional dependency
    YOLO = None

from ..config import get_settings
from ..utils.logger import setup_logger


logger = setup_logger()


class HeadDetectionService:
    def __init__(self) -> None:
        self.settings = get_settings()
        self.model = None
        self.model_loaded = False
        self.mock_mode = bool(self.settings.use_mock_detection)
        self.class_name = "head"
        self._load_model()

    def _load_model(self) -> None:
        model_path = self.settings.resolved_model_path
        if self.mock_mode:
            logger.warning("USE_MOCK_DETECTION is enabled. Running in demo mode.")
            return
        if YOLO is None:
            logger.warning("Ultralytics is not installed. Running in fallback demo mode.")
            self.mock_mode = True
            return
        if not model_path.exists():
            logger.warning("Head detector model not found at %s. Fallback demo mode is enabled.", model_path)
            self.mock_mode = True
            return
        try:
            self.model = YOLO(str(model_path))
            self.model_loaded = True
            names = getattr(self.model, "names", None)
            if names:
                self.class_name = list(names.values())[0] if isinstance(names, dict) else str(names[0])
            logger.info("Loaded head detection model from %s", model_path)
        except Exception as exc:
            logger.exception("Failed to load model: %s", exc)
            self.mock_mode = True

    def is_ready(self) -> bool:
        return self.model_loaded and not self.mock_mode

    def detect(self, frame) -> list[dict]:
        if self.mock_mode or self.model is None:
            return self._mock_detect(frame)

        try:
            results = self.model.predict(
                source=frame,
                conf=self.settings.confidence_threshold,
                imgsz=self.settings.image_size,
                verbose=False,
            )
            detections: list[dict] = []
            for result in results:
                if result.boxes is None:
                    continue
                for box in result.boxes:
                    cls_index = int(box.cls.item()) if box.cls is not None else 0
                    confidence = float(box.conf.item()) if box.conf is not None else 0.0
                    if confidence < self.settings.confidence_threshold:
                        continue
                    x1, y1, x2, y2 = [int(value) for value in box.xyxy[0].tolist()]
                    detections.append(
                        {
                            "bbox": {"x1": x1, "y1": y1, "x2": x2, "y2": y2},
                            "confidence": confidence,
                            "class_name": self.class_name if cls_index == 0 else self.class_name,
                            "track_id": 0,
                        }
                    )
            return detections
        except Exception as exc:
            logger.exception("Detection failed, switching to mock mode: %s", exc)
            self.mock_mode = True
            return self._mock_detect(frame)

    def _mock_detect(self, frame) -> list[dict]:
        """Use OpenCV Haar Cascade for face/head detection when YOLO is unavailable."""
        if frame is None or frame.size == 0:
            return []
        
        detections: list[dict] = []
        try:
            # Load OpenCV's face cascade classifier
            cascade_path = cv2.data.haarcascades + 'haarcascade_frontalface_default.xml'
            face_cascade = cv2.CascadeClassifier(cascade_path)
            
            # Convert frame to grayscale for better detection
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            
            # Detect faces
            faces = face_cascade.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=5, minSize=(30, 30))
            
            # Convert face detections to our format
            for x, y, w, h in faces:
                detections.append(
                    {
                        "bbox": {"x1": int(x), "y1": int(y), "x2": int(x + w), "y2": int(y + h)},
                        "confidence": round(random.uniform(0.75, 0.95), 2),
                        "class_name": "head",
                        "track_id": 0,
                    }
                )
        except Exception as exc:
            logger.warning("Cascade detection failed: %s. Using placeholder detections.", exc)
            # Fallback: generate 2 random boxes if cascade fails
            height, width = frame.shape[:2]
            for index in range(2):
                box_width = max(40, width // 12)
                box_height = max(50, height // 10)
                x1 = int((width * (0.2 + index * 0.22)) % max(width - box_width, 1))
                y1 = int(height * 0.2 + (index % 2) * 18)
                detections.append(
                    {
                        "bbox": {"x1": x1, "y1": y1, "x2": min(width - 1, x1 + box_width), "y2": min(height - 1, y1 + box_height)},
                        "confidence": round(random.uniform(0.72, 0.95), 2),
                        "class_name": "head",
                        "track_id": 0,
                    }
                )
        
        return detections
