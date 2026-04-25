# Deep Learning Based Head Detection System

Real-time head detection and counting system with a FastAPI backend and a React dashboard.

The backend reads camera frames, runs detection, tracks heads, computes stats, and streams updates over WebSocket. The frontend renders live boxes, head counts, FPS, logs, and charts.

## Highlights

- Real-time head detection from webcam, RTSP, or video file
- Live tracking labels and direction display (Left, Right, Up, Down, Forward)
- FastAPI REST API plus WebSocket live updates
- Detection log persistence in SQLite
- Directional model training support (single-class or multi-class)
- Graceful fallback mode when model weights are missing

## Tech Stack

- Backend: Python, FastAPI, Uvicorn, SQLAlchemy, OpenCV, Ultralytics YOLO
- Frontend: React, Vite, Tailwind CSS, Axios, Recharts
- Storage: SQLite

## Repository Structure

- backend: API, services, detection worker, training script
- frontend: dashboard UI and visualization components
- docs: API docs, system design, model and dataset guides
- models: model-related notes and assets
- sample_videos: sample video references

## Prerequisites

- Python 3.11+ recommended
- Node.js 18+ and npm
- Windows PowerShell, Command Prompt, or any shell
- Optional GPU for faster training/inference

## Quick Start

Run backend and frontend in separate terminals from project root.

### 1. Backend

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r backend/requirements.txt
cd backend
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### 2. Frontend

```bash
cd frontend
npm install
npm run dev
```

### 3. Open App

- Frontend: http://localhost:5173
- Backend: http://localhost:8000
- API Health: http://localhost:8000/api/health

## Camera Source Configuration

Set camera source with backend environment variable VIDEO_SOURCE.

- Webcam: 0
- RTSP: rtsp://username:password@ip-address:port/stream
- File: ./sample_videos/your_video.mp4

You can also start camera via API and pass source dynamically.

Example:

```bash
curl -X POST http://localhost:8000/api/camera/start \
	-H "Content-Type: application/json" \
	-d '{"source":"0"}'
```

## Model Weights

Default model path:

- backend/models/head_detector.pt

If weights are missing, backend starts in fallback detection mode so UI and pipeline can still be tested.

## Training

Training entry point:

- backend/train_head_detector.py

Supports two training modes:

- Single class: head
- Directional classes: head_forward, head_left, head_right, head_up, head_down

Directional training example:

```bash
python backend/train_head_detector.py \
	--data data/head_dataset.yaml \
	--model yolo11m.pt \
	--imgsz 1280 \
	--epochs 160 \
	--batch 8 \
	--device 0 \
	--directional-classes
```

More details: docs/MODEL_TRAINING_GUIDE.md

## Main API Endpoints

- GET /
- GET /api/health
- GET /api/camera/status
- POST /api/camera/start
- POST /api/camera/stop
- GET /api/camera/stream
- GET /api/detections/current
- GET /api/detections/logs
- GET /api/stats/summary
- GET /api/stats/timeline
- WS /ws/detections

Detailed reference: docs/API_DOCUMENTATION.md

## Key Backend Environment Variables

- APP_NAME
- HOST
- PORT
- DATABASE_URL
- MODEL_PATH
- VIDEO_SOURCE
- FRONTEND_URL
- CONFIDENCE_THRESHOLD
- IOU_THRESHOLD
- IMAGE_SIZE
- MAX_DETECTIONS
- MAX_FRAME_WIDTH
- USE_MOCK_DETECTION
- SAVE_DETECTION_LOGS

Example backend .env:

```env
APP_NAME=AI Head Counting CCTV System
HOST=0.0.0.0
PORT=8000
DATABASE_URL=sqlite:///./head_counting.db
MODEL_PATH=./models/head_detector.pt
VIDEO_SOURCE=0
FRONTEND_URL=http://localhost:5173
CONFIDENCE_THRESHOLD=0.35
IOU_THRESHOLD=0.45
IMAGE_SIZE=960
MAX_DETECTIONS=300
MAX_FRAME_WIDTH=1920
USE_MOCK_DETECTION=false
SAVE_DETECTION_LOGS=true
```

## Troubleshooting

- Frontend shows 404 on localhost:5173:
	- restart frontend with npm run dev from frontend directory
- Frontend cannot connect to backend:
	- ensure backend is running on port 8000
	- confirm FRONTEND_URL matches frontend origin
- No detections:
	- verify camera source and permissions
	- verify model exists at MODEL_PATH
	- check /api/health for model_loaded false
- Low FPS:
	- reduce IMAGE_SIZE
	- lower MAX_FRAME_WIDTH
	- use smaller model variant

## Documentation

- docs/README.md
- docs/API_DOCUMENTATION.md
- docs/SYSTEM_DESIGN.md
- docs/MODEL_TRAINING_GUIDE.md
- docs/DATASET_GUIDE.md
- docs/FUTURE_EXAM_MONITORING_FEATURES.md

## License

Add your preferred license information here.