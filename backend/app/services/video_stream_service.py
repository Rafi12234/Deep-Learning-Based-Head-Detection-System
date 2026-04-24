from __future__ import annotations

import cv2


def parse_source(source):
    if isinstance(source, str) and source.isdigit():
        return int(source)
    return source


class VideoStreamService:
    def __init__(self, source) -> None:
        self.source = parse_source(source)
        self.capture: cv2.VideoCapture | None = None
        self.width = 0
        self.height = 0

    def open(self) -> bool:
        if self.capture is not None and self.capture.isOpened():
            return True
        self.source = parse_source(self.source)
        self.capture = cv2.VideoCapture(self.source)
        if not self.capture.isOpened():
            return False
        self.width = int(self.capture.get(cv2.CAP_PROP_FRAME_WIDTH) or 0)
        self.height = int(self.capture.get(cv2.CAP_PROP_FRAME_HEIGHT) or 0)
        return True

    def read(self):
        if self.capture is None and not self.open():
            return False, None
        if self.capture is None:
            return False, None
        return self.capture.read()

    def release(self) -> None:
        if self.capture is not None:
            self.capture.release()
            self.capture = None
