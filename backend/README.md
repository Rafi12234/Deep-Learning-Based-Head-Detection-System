# Backend

FastAPI backend for the AI head counting CCTV system.

## Run Locally

```bash
pip install -r requirements.txt
copy .env.example .env
uvicorn app.main:app --reload
```

## API

- `GET /`
- `GET /api/health`
- `GET /api/camera/status`
- `POST /api/camera/start`
- `POST /api/camera/stop`
- `GET /api/detections/current`
- `GET /api/detections/logs`
- `GET /api/stats/summary`
- `GET /api/stats/timeline`
- `WS /ws/detections`

## Model

Place the trained model at `backend/models/head_detector.pt`. If it is missing, the app logs a warning and uses fallback demo detections.
