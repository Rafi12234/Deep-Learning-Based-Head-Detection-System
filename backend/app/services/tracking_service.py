from __future__ import annotations

import time

from ..config import get_settings
from ..utils.geometry import iou


class TrackingService:
    def __init__(self) -> None:
        self.settings = get_settings()
        self._next_track_id = 1
        self._tracks: dict[int, dict] = {}

    def update(self, detections: list[dict]) -> list[dict]:
        now = time.time()
        assigned: list[dict] = []
        used_track_ids: set[int] = set()

        for detection in detections:
            best_track_id = None
            best_score = 0.0
            for track_id, track in self._tracks.items():
                if track_id in used_track_ids:
                    continue
                score = iou(track["bbox"], detection["bbox"])
                if score > best_score:
                    best_track_id = track_id
                    best_score = score

            # Use 0.5 IOU threshold for stable tracking (same person across frames)
            if best_track_id is None or best_score < 0.5:
                best_track_id = self._next_track_id
                self._next_track_id += 1

            used_track_ids.add(best_track_id)
            self._tracks[best_track_id] = {"bbox": detection["bbox"], "last_seen": now}
            assigned.append({**detection, "track_id": best_track_id, "label": f"Head {best_track_id}"})

        timeout = self.settings.track_timeout_seconds
        self._tracks = {track_id: track for track_id, track in self._tracks.items() if now - track["last_seen"] <= timeout}
        return assigned
