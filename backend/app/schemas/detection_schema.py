from pydantic import BaseModel, Field


class BBoxSchema(BaseModel):
    x1: int
    y1: int
    x2: int
    y2: int


class CenterSchema(BaseModel):
    x: int
    y: int


class DetectionSchema(BaseModel):
    track_id: int = Field(default=0)
    label: str
    direction: str = "Forward"
    risk_status: str = "normal"
    side_look_duration_seconds: float =  0.0
    suspicious_side_look_count: int = 0
    potential_unethical: bool = False
    class_name: str = "head"
    confidence: float
    bbox: BBoxSchema
    center: CenterSchema


class DetectionUpdateSchema(BaseModel):
    type: str = "detection_update"
    timestamp: str
    frame_width: int
    frame_height: int
    total_heads: int
    fps: float
    camera_status: str
    potential_unethical_count: int = 0
    detections: list[DetectionSchema]


class DetectionLogResponse(BaseModel):
    id: int
    timestamp: str
    camera_id: int
    total_heads: int
    fps: float
    detections_json: dict
    frame_width: int
    frame_height: int
    created_at: str | None = None
