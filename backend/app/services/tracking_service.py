from __future__ import annotations

import time

from ..config import get_settings
from ..utils.geometry import iou, overlap_on_smaller_area


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
                score = self._match_score(track["bbox"], detection["bbox"])
                if score > best_score:
                    best_track_id = track_id
                    best_score = score

            # Allow a looser match so the same head keeps its ID while turning.
            if best_track_id is None or best_score < 0.25:
                best_track_id = self._next_track_id
                self._next_track_id += 1

            used_track_ids.add(best_track_id)
            self._tracks[best_track_id] = {
                "bbox": detection["bbox"],
                "last_seen": now,
                "confidence": float(detection.get("confidence", 0.0)),
                "class_name": detection.get("class_name", "head"),
                "pose_hint": detection.get("pose_hint", "forward"),
            }
            assigned.append({**detection, "track_id": best_track_id, "label": f"Head {best_track_id}"})

        timeout = self.settings.track_timeout_seconds
        active_tracks: dict[int, dict] = {}
        for track_id, track in self._tracks.items():
            age = now - track["last_seen"]
            if age <= timeout:
                active_tracks[track_id] = track
                if track_id not in used_track_ids:
                    assigned.append(
                        {
                            "bbox": track["bbox"],
                            "confidence": track.get("confidence", 0.0),
                            "class_name": track.get("class_name", "head"),
                            "pose_hint": track.get("pose_hint", "forward"),
                            "track_id": track_id,
                            "label": f"Head {track_id}",
                            "stale": True,
                        }
                    )

        self._tracks = active_tracks
        return self._deduplicate_visible_tracks(assigned)

    def _match_score(self, track_bbox: dict, detection_bbox: dict) -> float:
        overlap = iou(track_bbox, detection_bbox)
        track_center_x = (track_bbox["x1"] + track_bbox["x2"]) / 2
        track_center_y = (track_bbox["y1"] + track_bbox["y2"]) / 2
        det_center_x = (detection_bbox["x1"] + detection_bbox["x2"]) / 2
        det_center_y = (detection_bbox["y1"] + detection_bbox["y2"]) / 2

        track_width = max(1.0, float(track_bbox["x2"] - track_bbox["x1"]))
        track_height = max(1.0, float(track_bbox["y2"] - track_bbox["y1"]))
        distance_x = abs(det_center_x - track_center_x) / track_width
        distance_y = abs(det_center_y - track_center_y) / track_height
        center_score = max(0.0, 1.0 - ((distance_x + distance_y) / 2.0))

        return max(overlap, center_score)

    def _deduplicate_visible_tracks(self, detections: list[dict]) -> list[dict]:
        if len(detections) <= 1:
            return detections

        ordered = sorted(
            detections,
            key=lambda detection: (
                detection.get("stale", False),
                -float(detection.get("confidence", 0.0)),
            ),
        )
        kept: list[dict] = []
        for candidate in ordered:
            if any(self._is_duplicate_box(candidate["bbox"], existing["bbox"]) for existing in kept):
                continue
            kept.append(candidate)
        return kept

    def _is_duplicate_box(self, box_a: dict, box_b: dict) -> bool:
        # Catch nested stale/current duplicates in addition to regular overlap.
        return iou(box_a, box_b) >= 0.35 or overlap_on_smaller_area(box_a, box_b) >= 0.62
