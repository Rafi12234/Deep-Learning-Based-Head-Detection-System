from sqlalchemy import JSON, DateTime, Float, Integer, String, func
from sqlalchemy.orm import Mapped, mapped_column

from ..database import Base


class DetectionLog(Base):
    __tablename__ = "detection_logs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    timestamp: Mapped[str] = mapped_column(String(64), index=True)
    camera_id: Mapped[int] = mapped_column(Integer, index=True, default=1)
    total_heads: Mapped[int] = mapped_column(Integer, default=0)
    fps: Mapped[float] = mapped_column(Float, default=0.0)
    detections_json: Mapped[dict] = mapped_column(JSON, default=dict)
    frame_width: Mapped[int] = mapped_column(Integer, default=0)
    frame_height: Mapped[int] = mapped_column(Integer, default=0)
    created_at: Mapped[str] = mapped_column(DateTime(timezone=True), server_default=func.now())
