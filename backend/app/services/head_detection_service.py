from __future__ import annotations

import cv2

try:
    from ultralytics import YOLO
except Exception:  # pragma: no cover - optional dependency
    YOLO = None

from ..config import get_settings
from ..utils.geometry import iou, overlap_on_smaller_area
from ..utils.logger import setup_logger


logger = setup_logger()


class HeadDetectionService:
    def __init__(self) -> None:
        self.settings = get_settings()
        self.model = None
        self.model_loaded = False
        self.mock_mode = bool(self.settings.use_mock_detection)
        self.class_name = "head"
        self._class_names: dict[int, str] = {0: "head"}
        self._frontal_cascade = None
        self._frontal_alt_cascade = None
        self._profile_cascade = None
        self._mock_frame_index = 0
        self._load_model()
        self._load_mock_cascades()

    def _class_name_for_index(self, cls_index: int) -> str:
        return str(self._class_names.get(cls_index, self.class_name))

    def _pose_hint_from_class_name(self, class_name: str) -> str:
        normalized = str(class_name).strip().lower().replace("-", "_").replace(" ", "_")
        if "left" in normalized:
             return "left"
        if "right" in normalized:
            return "right"
        if "up" in normalized:
            return "up"
        if "down" in normalized:
            return "down"
        if "forward" in normalized or "front" in normalized:
            return "forward"
        return "forward"

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
            self.model =  YOLO(str(model_path))
            self.model_loaded = True
            names = getattr(self.model, "names", None)
            if names:
                if isinstance(names, dict):
                    self._class_names = {int(index): str(label) for index, label in names.items()}
                else:
                    self._class_names = {int(index): str(label) for index, label in enumerate(names)}
                self.class_name = self._class_names.get(0, "head")
            logger.info("Loaded head detection model from %s", model_path)
        except Exception as exc:
            logger.exception("Failed to load model: %s", exc)
            self.mock_mode = True

    def is_ready(self) -> bool:
        return self.model_loaded and not self.mock_mode

    def _load_mock_cascades(self) -> None:
        cascade_root = cv2.data.haarcascades
        self._frontal_cascade = cv2.CascadeClassifier(f"{cascade_root}haarcascade_frontalface_default.xml")
        self._frontal_alt_cascade = cv2.CascadeClassifier(f"{cascade_root}haarcascade_frontalface_alt2.xml")
        self._profile_cascade = cv2.CascadeClassifier(f"{cascade_root}haarcascade_profileface.xml")

    def _score_head_box(self, frame, bbox: dict, cascade_weight: float) -> float:
        height, width = frame.shape[:2]
        box_w = max(1, bbox["x2"] - bbox["x1"])
        box_h = max(1, bbox["y2"] - bbox["y1"])
        area_ratio = (box_w * box_h) / float(max(1, width * height))
        center_x = (bbox["x1"] + bbox["x2"]) / 2
        center_y = (bbox["y1"] + bbox["y2"]) / 2
        center_dx = abs(center_x - (width / 2)) / max(1.0, width / 2)
        center_dy = abs(center_y - (height / 2)) / max(1.0, height / 2)
        center_score = max(0.0, 1.0 - ((center_dx + center_dy) / 2.0))
        size_score = min(1.0, area_ratio * 18.0)
        return round(min(0.98, 0.45 + (cascade_weight * 0.18) + (size_score * 0.25) + (center_score * 0.12)), 2)

    def _append_cascade_detections(
        self,
        frame,
        gray,
        cascade,
        detections: list[dict],
        cascade_weight: float,
        *,
        mirrored: bool = False,
        pose_hint: str = "forward",
        scale_to_full: float = 1.0,
    ) -> None:
        if cascade is None or cascade.empty():
            return

        faces = cascade.detectMultiScale(
            gray,
            scaleFactor=1.08,
            minNeighbors=7,
            minSize=(44, 44),
        )
        detect_width = gray.shape[1]

        for x, y, w, h in faces:
            if mirrored:
                x = detect_width - (x + w)

            bbox = {
                "x1": int(x * scale_to_full),
                "y1": int(y * scale_to_full),
                "x2": int((x + w) * scale_to_full),
                "y2": int((y + h) * scale_to_full),
            }
            if not self._is_valid_head_box(frame, bbox):
                continue

            detections.append(
                {
                    "bbox": bbox,
                    "confidence": self._score_head_box(frame, bbox, cascade_weight),
                    "class_name": "head",
                    "pose_hint": pose_hint,
                    "track_id": 0,
                }
            )

    def detect(self, frame) -> list[dict]:
        if self.mock_mode or self.model is None:
            return self._mock_detect(frame)

        try:
            results = self.model.predict(
                source=frame,
                conf=self.settings.confidence_threshold,
                iou=self.settings.iou_threshold,
                imgsz=self.settings.image_size,
                max_det=self.settings.max_detections,
                agnostic_nms=self.settings.agnostic_nms,
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
                    class_name = self._class_name_for_index(cls_index)
                    detections.append(
                        {
                            "bbox": {"x1": x1, "y1": y1, "x2": x2, "y2": y2},
                            "confidence": confidence,
                            "class_name": class_name,
                            "pose_hint": self._pose_hint_from_class_name(class_name),
                            "track_id": 0,
                        }
                    )
            return self._suppress_duplicates(detections)
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
            self._mock_frame_index += 1

            # Convert frame to grayscale for better detection
            gray_full = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

            # Speed up fallback mode by running cascades on a downscaled frame.
            mock_scale = 0.75
            gray = cv2.resize(gray_full, None, fx=mock_scale, fy=mock_scale, interpolation=cv2.INTER_AREA)
            scale_to_full = 1.0 / mock_scale

            self._append_cascade_detections(
                frame,
                gray,
                self._frontal_cascade,
                detections,
                1.0,
                pose_hint="forward",
                scale_to_full=scale_to_full,
            )
            self._append_cascade_detections(
                frame,
                gray,
                self._frontal_alt_cascade,
                detections,
                0.9,
                pose_hint="forward",
                scale_to_full=scale_to_full,
            )

            # Profile cascades are expensive; run every third frame to recover FPS.
            if self._mock_frame_index % 3 == 0:
                profile_gray = cv2.equalizeHist(gray)
                self._append_cascade_detections(
                    frame,
                    profile_gray,
                    self._profile_cascade,
                    detections,
                    0.85,
                    pose_hint="right",
                    scale_to_full=scale_to_full,
                )

                flipped_gray = cv2.flip(profile_gray, 1)
                self._append_cascade_detections(
                    frame,
                    flipped_gray,
                    self._profile_cascade,
                    detections,
                    0.85,
                    mirrored=True,
                    pose_hint="left",
                    scale_to_full=scale_to_full,
                )
        except Exception as exc:
            logger.warning("Cascade detection failed: %s. Using placeholder detections.", exc)
            return []
        
        return self._suppress_duplicates(detections)

    def _is_valid_head_box(self, frame, bbox: dict) -> bool:
        height, width = frame.shape[:2]
        box_w = max(0, bbox["x2"] - bbox["x1"])
        box_h = max(0, bbox["y2"] - bbox["y1"])
        if box_w < 48 or box_h < 48:
            return False

        area_ratio = (box_w * box_h) / float(max(1, width * height))
        if area_ratio < 0.01:
            return False

        aspect_ratio = box_w / float(max(1, box_h))
        if aspect_ratio < 0.55 or aspect_ratio > 1.75:
            return False

        return True

    def _suppress_duplicates(self, detections: list[dict]) -> list[dict]:
        if len(detections) <= 1:
            return detections

        # Keep the highest-confidence detection first, then discard near-duplicates.
        ordered = sorted(detections, key=lambda detection: detection.get("confidence", 0.0), reverse=True)
        kept: list[dict] = []
        for candidate in ordered:
            if any(self._is_duplicate_box(candidate["bbox"], existing["bbox"]) for existing in kept):
                continue
            kept.append(candidate)
        return kept

    def _is_duplicate_box(self, box_a: dict, box_b: dict) -> bool:
        # Remove both conventional overlaps and nested (inside) duplicates.
        return iou(box_a, box_b) >= 0.35 or overlap_on_smaller_area(box_a, box_b) >= 0.62
