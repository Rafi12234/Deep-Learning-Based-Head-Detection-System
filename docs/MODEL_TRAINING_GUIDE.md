# Model Training Guide

This project supports two training modes:

- Single-class detection: `head`
- Directional multi-class detection:
	- `head_forward`
	- `head_left`
	- `head_right`
	- `head_up`
	- `head_down`

If you want highly accurate direction labels (especially up/down), use directional multi-class training.

## Recommended Datasets

- SCUT-HEAD
- CrowdHuman head annotations
- Custom exam hall CCTV frames

## Annotation Rules

- Draw the box only around the visible head
- Keep labels consistent with your selected mode:
	- single-class: always `head`
	- directional mode: one of `head_forward/head_left/head_right/head_up/head_down`
- Use crowded and partially occluded examples

For directional mode, include many static (not moving) up/down poses so the model learns pitch directly.

## Recommended Settings

- Image size: `960` or `1280`
- Model size: `YOLO11s` for speed, `YOLO11m` for accuracy
- Save the trained model as `backend/models/head_detector.pt`

## High-Density (50+ Heads) Training

To reliably detect many heads in one frame, you must train on crowded scenes with small and partially occluded heads.

1. Prepare YOLO dataset YAML (`data/head_dataset.yaml`) with:
	- single-class mode: `names: [head]`
	- directional mode:
	  - `names: [head_forward, head_left, head_right, head_up, head_down]`
	- train/val/test splits
	- crowded classroom/exam hall examples
2. Install backend dependencies:
	- `pip install -r backend/requirements.txt`
3. Run training (from project root):
	- single-class:
	  - `python backend/train_head_detector.py --data data/head_dataset.yaml --model yolo11m.pt --imgsz 1280 --epochs 140 --batch 8 --device 0`
	- directional multi-class:
	  - `python backend/train_head_detector.py --data data/head_dataset.yaml --model yolo11m.pt --imgsz 1280 --epochs 160 --batch 8 --device 0 --directional-classes`
4. After training, copy best model:
	- `runs/head-train/head-yolo11m-dense/weights/best.pt -> backend/models/head_detector.pt`
5. Restart backend and confirm:
	- `/api/health` returns `"model_loaded": true`

## Runtime Tuning For 50+ Heads

Set these environment variables in backend `.env`:

- `IMAGE_SIZE=1280`
- `MAX_DETECTIONS=300`
- `IOU_THRESHOLD=0.45`
- `CONFIDENCE_THRESHOLD=0.25`
- `MAX_FRAME_WIDTH=1920`

If false positives increase, raise `CONFIDENCE_THRESHOLD` gradually to `0.30-0.35`.

## Notes

Normal person detection is not the final solution for crowded exam hall head counting. Use a dedicated head detector for best results.

Directional note: when using directional classes, horizontal flip augmentation is disabled by the training script to avoid learning wrong left/right labels.
