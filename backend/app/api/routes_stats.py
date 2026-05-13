from fastapi import APIRouter, Depends

from ..database import check_database
from ..schemas.camera_schema import HealthResponse
from ..workers.camera_worker import CameraWorker


router = APIRouter(prefix="/api/stats",  tags=["stats"])


def get_worker() -> CameraWorker:
    from ..main import camera_worker

    return camera_worker


@router.get("/summary")
def stats_summary(worker: CameraWorker = Depends(get_worker)):
    return worker.get_summary()


@router.get("/timeline")
def stats_timeline(worker: CameraWorker = Depends(get_worker)):
    return {"items": worker.get_timeline()}


@router.get("/health", response_model=HealthResponse)
def stats_health(worker: CameraWorker = Depends(get_worker)):
    return HealthResponse(status="ok", model_loaded=worker.detection_service.is_ready(), database_connected=check_database())
