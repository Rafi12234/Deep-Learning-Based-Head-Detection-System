from fastapi import APIRouter, Depends, Query

from ..schemas.detection_schema import DetectionUpdateSchema
from ..workers.camera_worker import CameraWorker


router = APIRouter(prefix="/api/detections", tags=["detections"])


def get_worker() ->  CameraWorker:
    from ..main import camera_worker

    return camera_worker


@router.get("/current", response_model=DetectionUpdateSchema)
def current_detections(worker: CameraWorker = Depends(get_worker)):
    return worker.get_current_data()


@router.get("/logs")
def detection_logs(limit: int = Query(default=50, ge=1, le=200), offset: int = Query(default=0, ge=0), worker: CameraWorker = Depends(get_worker)):
    logs = worker.get_logs(limit=limit, offset=offset)
    return {"items": logs, "limit": limit, "offset": offset, "count": len(logs)}
