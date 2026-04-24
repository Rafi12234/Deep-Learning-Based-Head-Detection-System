from __future__ import annotations

from contextlib import asynccontextmanager
import asyncio

from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware

from .api.routes_camera import router as camera_router
from .api.routes_detection import router as detection_router
from .api.routes_stats import router as stats_router
from .config import get_settings
from .database import check_database, init_db
from .services.websocket_manager import WebSocketManager
from .utils.logger import setup_logger
from .workers.camera_worker import CameraWorker


settings = get_settings()
logger = setup_logger()
websocket_manager = WebSocketManager()
camera_worker = CameraWorker(websocket_manager)


@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    logger.info("Database ready: %s", check_database())
    yield
    camera_worker.stop()


app = FastAPI(title=settings.app_name, lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[settings.frontend_url, "http://localhost:5173", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(camera_router)
app.include_router(detection_router)
app.include_router(stats_router)


@app.get("/")
def root():
    return {"message": "AI Head Counting CCTV System backend is running."}


@app.get("/api/health")
def health():
    return {
        "status": "ok",
        "model_loaded": camera_worker.detection_service.is_ready(),
        "database_connected": check_database(),
    }


@app.websocket("/ws/detections")
async def detections_socket(websocket: WebSocket):
    websocket_manager.set_loop(asyncio.get_running_loop())
    await websocket_manager.connect(websocket)
    try:
        await websocket.send_json(camera_worker.get_current_data())
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        websocket_manager.disconnect(websocket)
    except Exception:
        websocket_manager.disconnect(websocket)
