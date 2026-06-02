from fastapi import APIRouter, Depends
from fastapi.responses import StreamingResponse

from ..schemas.camera_schema import CameraControlRequest, CameraStatusResponse
from ..workers.camera_worker import CameraWorker


router = APIRouter(prefix="/api/camera", tags=["camera"])


def get_worker() -> CameraWorker:
    from ..main import camera_worker
    

    return camera_worker


@router.get("/status", response_model=CameraStatusResponse)
def camera_status(worker: CameraWorker = Depends(get_worker)):
    return worker.get_status()


@router.post("/start")
def start_camera(payload: CameraControlRequest | None = None, worker: CameraWorker =  Depends(get_worker)):
    source = payload.source if payload else None
    return worker.start(source=source)


@router.post("/stop")
def stop_camera(worker: CameraWorker = Depends(get_worker)):
    return worker.stop()


@router.get("/stream")
def stream_camera(worker: CameraWorker = Depends(get_worker)):
    boundary = b"--frame\r\n"

    def frame_generator():
        import time

        while True:
            frame_bytes = worker.get_latest_frame_bytes()
            if frame_bytes:
                yield boundary + b"Content-Type: image/jpeg\r\n\r\n" + frame_bytes +  b"\r\n"
            else:
                time.sleep(0.2)

    return StreamingResponse(frame_generator(), media_type="multipart/x-mixed-replace; boundary=frame")
