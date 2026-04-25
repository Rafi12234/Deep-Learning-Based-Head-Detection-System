from __future__ import annotations

import threading
import time
from datetime import datetime, timezone

import cv2
from sqlalchemy import select

from ..config import get_settings
from ..database import SessionLocal
from ..models.camera import Camera
from ..models.detection_log import DetectionLog
from ..services.counting_service import CountingService
from ..services.head_detection_service import HeadDetectionService
from ..services.tracking_service import TrackingService
from ..services.video_stream_service import VideoStreamService
from ..services.websocket_manager import WebSocketManager
from ..services.video_stream_service import parse_source
from ..utils.logger import setup_logger


logger = setup_logger()


class CameraWorker:
    def __init__(self, websocket_manager: WebSocketManager) -> None:
        self.settings = get_settings()
        self.websocket_manager = websocket_manager
        self.detection_service = HeadDetectionService()
        self.tracking_service = TrackingService()
        self.counting_service = CountingService()
        self.video_service = VideoStreamService(self.settings.parsed_video_source)
        self._thread: threading.Thread | None = None
        self._running = threading.Event()
        self._state_lock = threading.Lock()
        self._current_payload: dict = self._empty_payload()
        self._latest_frame_bytes: bytes | None = None
        self._last_log_time = 0.0
        self._camera_status = "stopped"
        self._track_direction_state: dict[int, dict] = {}

    def _empty_payload(self) -> dict:
        return {
            "type": "detection_update",
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "frame_width": 0,
            "frame_height": 0,
            "total_heads": 0,
            "fps": 0.0,
            "camera_status": "stopped",
            "detections": [],
        }

    def start(self, source=None) -> dict:
        if self._running.is_set():
            if self._camera_status == "disconnected":
                if source is not None:
                    self.video_service.source = parse_source(source)
                self.video_service.release()
                self._camera_status = "running"
                self._store_camera_status()
                return {"status": "restarting"}
            return {"status": "already_running"}

        if source is not None:
            self.video_service.source = parse_source(source)

        if not self.video_service.open():
            self._camera_status = "disconnected"
            self._store_camera_status()
            self._running.set()
            self._thread = threading.Thread(target=self._run, daemon=True)
            self._thread.start()
            return {"status": "started_with_disconnected_source"}

        self._running.set()
        self._camera_status = "running"
        self._store_camera_status()
        self._thread = threading.Thread(target=self._run, daemon=True)
        self._thread.start()
        return {"status": "started"}

    def stop(self) -> dict:
        self._running.clear()
        self._camera_status = "stopped"
        self.video_service.release()
        self._store_camera_status()
        if self._thread and self._thread.is_alive():
            self._thread.join(timeout=1.0)
        return {"status": "stopped"}

    def get_status(self) -> dict:
        return {
            "camera_id": 1,
            "name": "Primary Camera",
            "source": str(self.video_service.source),
            "status": self._camera_status,
            "location": "N/A",
        }

    def get_current_data(self) -> dict:
        with self._state_lock:
            return self._current_payload

    def get_latest_frame_bytes(self) -> bytes | None:
        with self._state_lock:
            return self._latest_frame_bytes

    def get_summary(self) -> dict:
        return self.counting_service.summary()

    def get_timeline(self) -> list[dict]:
        return self.counting_service.timeline()

    def get_logs(self, limit: int = 50, offset: int = 0) -> list[dict]:
        with SessionLocal() as session:
            statement = select(DetectionLog).order_by(DetectionLog.id.desc()).offset(offset).limit(limit)
            rows = session.execute(statement).scalars().all()
            return [
                {
                    "id": row.id,
                    "timestamp": row.timestamp,
                    "camera_id": row.camera_id,
                    "total_heads": row.total_heads,
                    "fps": row.fps,
                    "detections_json": row.detections_json,
                    "frame_width": row.frame_width,
                    "frame_height": row.frame_height,
                    "created_at": row.created_at.isoformat() if row.created_at else None,
                }
                for row in rows
            ]

    def _run(self) -> None:
        last_frame_time = time.perf_counter()
        while self._running.is_set():
            ok, frame = self.video_service.read()
            if not ok or frame is None:
                self._camera_status = "disconnected"
                self._store_camera_status()
                time.sleep(0.3)
                continue

            now = time.perf_counter()
            delta = now - last_frame_time
            fps = 1.0 / delta if delta > 0 else 0.0
            last_frame_time = now

            target_max_width = self.settings.max_frame_width
            if self.detection_service.mock_mode:
                # Fallback cascades are CPU-heavy; cap width for smoother real-time FPS.
                target_max_width = min(target_max_width, 960)

            if frame.shape[1] > target_max_width:
                scale = target_max_width / frame.shape[1]
                frame = cv2.resize(frame, (target_max_width, int(frame.shape[0] * scale)))

            raw_detections = self.detection_service.detect(frame)
            tracked_detections = self.tracking_service.update(raw_detections)
            self._assign_display_labels(tracked_detections, frame.shape[1], frame.shape[0])
            timestamp = datetime.now(timezone.utc).isoformat()
            self.counting_service.update(tracked_detections, fps, timestamp)

            self._update_state(frame, tracked_detections, fps, timestamp)
            self._maybe_save_log()

            payload = self.get_current_data()
            self.websocket_manager.broadcast_threadsafe(payload)

        self.video_service.release()

    def _assign_display_labels(self, detections: list[dict], frame_width: int, frame_height: int) -> None:
        # Display labels are re-numbered for each frame as Head 1..N.
        detections.sort(key=lambda detection: (detection["bbox"]["x1"], detection["bbox"]["y1"]))
        active_track_ids: set[int] = set()
        for index, detection in enumerate(detections, start=1):
            detection["label"] = f"Head {index}"
            detection["direction"] = self._infer_direction(detection, frame_width, frame_height)
            active_track_ids.add(int(detection.get("track_id", -1)))

        # Keep per-track direction state only for tracks visible in this frame.
        self._track_direction_state = {
            track_id: state
            for track_id, state in self._track_direction_state.items()
            if track_id in active_track_ids
        }

    def _infer_direction(self, detection: dict, frame_width: int, frame_height: int) -> str:
        bbox = detection.get("bbox", {})
        center_x = (bbox.get("x1", 0) + bbox.get("x2", 0)) / 2
        center_y = (bbox.get("y1", 0) + bbox.get("y2", 0)) / 2
        bbox_width = max(1.0, float(bbox.get("x2", 0) - bbox.get("x1", 0)))
        bbox_height = max(1.0, float(bbox.get("y2", 0) - bbox.get("y1", 0)))

        area_ratio = (bbox_width * bbox_height) / max(1.0, float(frame_width * frame_height))
        track_id = int(detection.get("track_id", -1))

        pose_hint = str(detection.get("pose_hint", "forward")).lower()

        # Trust class-based directional hints whenever available.
        if pose_hint == "left":
            direction = "Left"
        elif pose_hint == "right":
            direction = "Right"
        elif pose_hint == "up":
            direction = "Up"
        elif pose_hint == "down":
            direction = "Down"
        else:
            direction = "Forward"

        previous = self._track_direction_state.get(track_id)
        baseline_y = center_y
        if previous:
            dy_ratio = (center_y - float(previous.get("center_y", center_y))) / max(1.0, float(frame_height))
            baseline_y = float(previous.get("baseline_y", center_y))
            y_offset_ratio = (center_y - baseline_y) / max(1.0, float(frame_height))

            # For frontal faces, classify from both movement and persistent vertical offset
            # relative to each track's neutral baseline.
            if pose_hint == "forward":
                if dy_ratio <= -0.025 or y_offset_ratio <= -0.06:
                    direction = "Up"
                elif dy_ratio >= 0.025 or y_offset_ratio >= 0.06:
                    direction = "Down"
                elif abs(y_offset_ratio) <= 0.03:
                    direction = "Forward"
                else:
                    direction = str(previous.get("direction", "Forward"))

                # Keep a stable neutral baseline. Update quickly in neutral state,
                # and very slowly in non-neutral state to avoid drift.
                baseline_alpha = 0.08 if direction == "Forward" else 0.01
                baseline_y = ((1.0 - baseline_alpha) * baseline_y) + (baseline_alpha * center_y)

        self._track_direction_state[track_id] = {
            "center_x": center_x,
            "center_y": center_y,
            "area_ratio": area_ratio,
            "baseline_y": baseline_y,
            "direction": direction,
        }

        if direction in {"Left", "Right", "Up", "Down", "Forward"}:
            return direction
        return "Forward"

    def _update_state(self, frame, detections: list[dict], fps: float, timestamp: str) -> None:
        success, encoded = cv2.imencode(".jpg", frame)
        frame_bytes = encoded.tobytes() if success else None
        payload = {
            "type": "detection_update",
            "timestamp": timestamp,
            "frame_width": int(frame.shape[1]),
            "frame_height": int(frame.shape[0]),
            "total_heads": len(detections),
            "fps": round(fps, 2),
            "camera_status": self._camera_status,
            "detections": [
                {
                    "track_id": detection["track_id"],
                    "label": detection["label"],
                    "direction": detection.get("direction", "Forward"),
                    "class_name": detection.get("class_name", "head"),
                    "confidence": round(float(detection.get("confidence", 0.0)), 2),
                    "bbox": detection["bbox"],
                    "center": {
                        "x": int((detection["bbox"]["x1"] + detection["bbox"]["x2"]) / 2),
                        "y": int((detection["bbox"]["y1"] + detection["bbox"]["y2"]) / 2),
                    },
                }
                for detection in detections
            ],
        }
        with self._state_lock:
            self._current_payload = payload
            self._latest_frame_bytes = frame_bytes
        self._camera_status = "running"

    def _maybe_save_log(self) -> None:
        if not self.settings.save_detection_logs:
            return
        now = time.time()
        if now - self._last_log_time < self.settings.detection_log_interval_seconds:
            return
        self._last_log_time = now
        payload = self.get_current_data()
        with SessionLocal() as session:
            session.add(
                DetectionLog(
                    timestamp=payload["timestamp"],
                    camera_id=1,
                    total_heads=payload["total_heads"],
                    fps=payload["fps"],
                    detections_json=payload,
                    frame_width=payload["frame_width"],
                    frame_height=payload["frame_height"],
                )
            )
            session.commit()

    def _store_camera_status(self) -> None:
        with SessionLocal() as session:
            camera = session.get(Camera, 1)
            if camera is None:
                camera = Camera(id=1, name="Primary Camera", source=str(self.video_service.source), status=self._camera_status, location="N/A")
                session.add(camera)
            else:
                camera.source = str(self.video_service.source)
                camera.status = self._camera_status
            session.commit()
