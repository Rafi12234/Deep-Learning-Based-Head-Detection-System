from functools import lru_cache
from pathlib import Path

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    app_name: str = Field(default="AI Head Counting CCTV System", alias="APP_NAME")
    app_env: str = Field(default="development", alias="APP_ENV")
    host: str = Field(default="0.0.0.0", alias="HOST")
    port: int = Field(default=8000, alias="PORT")

    database_url: str = Field(default="sqlite:///./head_counting.db", alias="DATABASE_URL")
    model_path: str = Field(default="./models/head_detector.pt", alias="MODEL_PATH")
    tracker_type: str = Field(default="bytetrack.yaml", alias="TRACKER_TYPE")
    confidence_threshold: float = Field(default=0.35, alias="CONFIDENCE_THRESHOLD")
    iou_threshold: float = Field(default=0.45, alias="IOU_THRESHOLD")
    image_size: int = Field(default=960, alias="IMAGE_SIZE")
    max_detections: int = Field(default=300, alias="MAX_DETECTIONS")
    agnostic_nms: bool = Field(default=True, alias="AGNOSTIC_NMS")

    video_source: str = Field(default="0", alias="VIDEO_SOURCE")
    use_mock_detection: bool = Field(default=False, alias="USE_MOCK_DETECTION")
    save_detection_logs: bool = Field(default=True, alias="SAVE_DETECTION_LOGS")

    frontend_url: str = Field(default="http://localhost:5173", alias="FRONTEND_URL")
    detection_log_interval_seconds: int = 3
    track_timeout_seconds: float = 4.0
    max_frame_width: int = 1920

    @property
    def resolved_model_path(self) -> Path:
        return Path(self.model_path).expanduser().resolve()

    @property
    def parsed_video_source(self):
        source = self.video_source
        if isinstance(source, str) and source.isdigit():
            return int(source)
        return source


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    return Settings()
