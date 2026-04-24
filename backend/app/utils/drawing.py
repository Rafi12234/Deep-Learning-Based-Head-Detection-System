from __future__ import annotations

import cv2


def draw_detections(frame, detections: list[dict]):
    for detection in detections:
        bbox = detection["bbox"]
        label = detection.get("label", f'Head {detection.get("track_id", 0)}')
        confidence = detection.get("confidence", 0.0)

        color = (0, 0, 255)
        cv2.rectangle(frame, (bbox["x1"], bbox["y1"]), (bbox["x2"], bbox["y2"]), color, 2)
        text = f"{label} {confidence:.2f}"
        y_text = max(18, bbox["y1"] - 8)
        cv2.putText(frame, text, (bbox["x1"], y_text), cv2.FONT_HERSHEY_SIMPLEX, 0.55, color, 2, cv2.LINE_AA)
    return frame
