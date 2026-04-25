from __future__ import annotations

import argparse
from pathlib import Path


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Train a high-density YOLO head detector.")
    parser.add_argument("--data", required=True, help="Path to dataset YAML (YOLO format).")
    parser.add_argument("--model", default="yolo11m.pt", help="Base model checkpoint.")
    parser.add_argument("--epochs", type=int, default=140, help="Training epochs.")
    parser.add_argument("--imgsz", type=int, default=1280, help="Training/inference image size.")
    parser.add_argument("--batch", type=int, default=8, help="Batch size (reduce if OOM).")
    parser.add_argument("--device", default="0", help="CUDA device id or 'cpu'.")
    parser.add_argument("--workers", type=int, default=8, help="Data loader workers.")
    parser.add_argument("--project", default="runs/head-train", help="Output project directory.")
    parser.add_argument("--name", default="head-yolo11m-dense", help="Training run name.")
    parser.add_argument(
        "--directional-classes",
        action="store_true",
        help=(
            "Enable if dataset has classes like head_forward/head_left/head_right/head_up/head_down. "
            "Disables horizontal flips to prevent left/right label corruption."
        ),
    )
    return parser.parse_args()


def main() -> None:
    try:
        from ultralytics import YOLO
    except Exception as exc:  # pragma: no cover
        raise SystemExit("Ultralytics is required. Install with: pip install ultralytics") from exc

    args = parse_args()
    data_path = Path(args.data).expanduser().resolve()
    if not data_path.exists():
        raise SystemExit(f"Dataset YAML not found: {data_path}")

    model = YOLO(args.model)
    fliplr = 0.0 if args.directional_classes else 0.5
    model.train(
        data=str(data_path),
        epochs=args.epochs,
        imgsz=args.imgsz,
        batch=args.batch,
        device=args.device,
        workers=args.workers,
        optimizer="AdamW",
        lr0=0.001,
        lrf=0.01,
        weight_decay=0.0005,
        hsv_h=0.01,
        hsv_s=0.5,
        hsv_v=0.3,
        degrees=5.0,
        translate=0.08,
        scale=0.35,
        shear=1.5,
        perspective=0.0005,
        flipud=0.0,
        fliplr=fliplr,
        mosaic=1.0,
        close_mosaic=12,
        mixup=0.05,
        copy_paste=0.0,
        project=args.project,
        name=args.name,
        pretrained=True,
        cache=True,
        plots=True,
    )

    print("Training finished.")
    print("Use best.pt from the run directory as backend/models/head_detector.pt")


if __name__ == "__main__":
    main()
