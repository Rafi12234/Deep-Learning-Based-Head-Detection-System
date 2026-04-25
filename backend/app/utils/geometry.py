from __future__ import annotations


def bbox_center(bbox: dict) -> tuple[int, int]:
    return (int((bbox["x1"] + bbox["x2"]) / 2), int((bbox["y1"] + bbox["y2"]) / 2))


def bbox_area(bbox: dict) -> int:
    return max(0, bbox["x2"] - bbox["x1"]) * max(0, bbox["y2"] - bbox["y1"])


def intersection_area(box_a: dict, box_b: dict) -> int:
    x_left = max(box_a["x1"], box_b["x1"])
    y_top = max(box_a["y1"], box_b["y1"])
    x_right = min(box_a["x2"], box_b["x2"])
    y_bottom = min(box_a["y2"], box_b["y2"])

    if x_right <= x_left or y_bottom <= y_top:
        return 0

    return (x_right - x_left) * (y_bottom - y_top)


def overlap_on_smaller_area(box_a: dict, box_b: dict) -> float:
    intersection = intersection_area(box_a, box_b)
    min_area = min(bbox_area(box_a), bbox_area(box_b))
    return (intersection / min_area) if min_area else 0.0


def iou(box_a: dict, box_b: dict) -> float:
    intersection = intersection_area(box_a, box_b)
    if not intersection:
        return 0.0

    union = bbox_area(box_a) + bbox_area(box_b) - intersection
    return intersection / union if union else 0.0
