from __future__ import annotations


class CountingService:
    def __init__(self) -> None:
        self.total_frames = 0
        self.max_head_count = 0
        self._head_count_sum = 0
        self._fps_sum = 0.0
        self.current_heads = 0
        self.current_track_ids: list[int] = []
        self.entered_count = 0
        self.exited_count = 0
        self.zone_count = 0
        self._previous_track_ids: set[int] = set()
        self.history: list[dict] = []

    def update(self, detections: list[dict], fps: float, timestamp: str) -> dict:
        current_track_ids = {detection["track_id"] for detection in detections}
        entered = len(current_track_ids - self._previous_track_ids)
        exited = len(self._previous_track_ids - current_track_ids)

        self.entered_count += entered
        self.exited_count += exited
        self.total_frames += 1
        self.current_heads = len(detections)
        self.current_track_ids = sorted(current_track_ids)
        self.max_head_count = max(self.max_head_count, self.current_heads)
        self._head_count_sum += self.current_heads
        self._fps_sum += fps
        self._previous_track_ids = current_track_ids

        snapshot = {
            "timestamp": timestamp,
            "total_heads": self.current_heads,
            "fps": round(fps, 2),
            "entered_count": self.entered_count,
            "exited_count": self.exited_count,
            "zone_count": self.zone_count,
            "active_track_ids": list(self.current_track_ids),
        }
        self.history.append(snapshot)
        self.history = self.history[-200:]
        return snapshot

    def summary(self) -> dict:
        average_head_count = self._head_count_sum / self.total_frames if self.total_frames else 0.0
        average_fps = self._fps_sum / self.total_frames if self.total_frames else 0.0
        last_update = self.history[-1]["timestamp"] if self.history else None
        return {
            "total_processed_frames": self.total_frames,
            "average_head_count": round(average_head_count, 2),
            "max_head_count": self.max_head_count,
            "average_fps": round(average_fps, 2),
            "last_update_time": last_update,
        }

    def timeline(self) -> list[dict]:
        return self.history
