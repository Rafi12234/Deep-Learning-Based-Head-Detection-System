# AI Head Counting CCTV System

Real-time AI CCTV monitoring system for detecting and counting visible human heads in live webcam, RTSP, or video-file feeds. The backend streams detections through WebSocket and the React dashboard overlays bounding boxes, track IDs, counts, FPS, and logs.

## Features

- Real-time head detection from webcam, RTSP, or local video
- Stable tracking IDs like Head 1, Head 2, Head 3
- WebSocket detection updates for the React dashboard
- SQLite logging for detection events and camera state
- Optional line or zone counting structure
- Fallback demo mode when the custom model is missing
- Extensible architecture for future exam monitoring features

## Tech Stack

- Backend: Python, FastAPI, WebSocket, OpenCV, Ultralytics YOLO, SQLite, SQLAlchemy, Pydantic, Uvicorn
- Frontend: React, Vite, Tailwind CSS, Axios, React Router, Recharts

## Folder Structure

- backend: FastAPI app, services, database, and API routes
- frontend: React dashboard, live monitor, logs, and settings pages
- docs: model training, dataset guidance, and system design notes

## Setup

### Backend

```bash
cd backend
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
copy .env.example .env
uvicorn app.main:app --reload
```

### Frontend

```bash
cd frontend
npm install
copy .env.example .env
npm run dev
```

## How to Run

1. Start the backend on port 8000.
2. Start the frontend on port 5173.
3. Open the React dashboard.
4. Click Start Camera.
5. View live detections, counts, and logs.

## Camera Sources

Use `VIDEO_SOURCE` in the backend `.env` file.

- Webcam: `0`
- RTSP: `rtsp://username:password@ip-address:port/stream`
- Video file: `./sample_videos/exam_hall.mp4`

## YOLO Model Placement

Place your trained head detector here:

- `backend/models/head_detector.pt`

If the file is missing, the backend starts in fallback demo mode so the frontend can still be tested.

## Real-Time Flow

Camera feed -> frame reader -> head detector -> tracker -> counter -> WebSocket -> React dashboard -> SQLite logs

## Troubleshooting

- If the model is missing, check `backend/.env` and the model path.
- If RTSP fails, verify the stream URL and network access.
- If the frontend cannot connect, confirm the API and WebSocket URLs in `frontend/.env`.
- On slower machines, reduce `IMAGE_SIZE` or use a smaller YOLO model.

