from pydantic import BaseModel, Field


class CameraControlRequest(BaseModel):
    camera_id: int = Field(default=1)
    source: str | int | None = None
    name: str | None = None


class CameraStatusResponse(BaseModel):
    camera_id: int
    name: str
    source: str
    status: str
    location: str = "N/A"


class HealthResponse(BaseModel):
    status: str
    model_loaded: bool
    database_connected: bool
