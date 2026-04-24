# API Documentation

## REST Endpoints

- `GET /` health message
- `GET /api/health` backend, model, and database status
- `GET /api/camera/status` camera source status
- `POST /api/camera/start` start camera processing
- `POST /api/camera/stop` stop camera processing
- `GET /api/detections/current` current live detection payload
- `GET /api/detections/logs` paginated logs
- `GET /api/stats/summary` summary statistics
- `GET /api/stats/timeline` chart data

## WebSocket

- `WS /ws/detections`

Each message follows the detection update structure used by the dashboard.
