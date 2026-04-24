# Model Training Guide

This project works best with a custom YOLO model trained for one class:

- `head`

## Recommended Datasets

- SCUT-HEAD
- CrowdHuman head annotations
- Custom exam hall CCTV frames

## Annotation Rules

- Draw the box only around the visible head
- Keep labels consistent as `head`
- Use crowded and partially occluded examples

## Recommended Settings

- Image size: `960` or `1280`
- Model size: `YOLO11s` for speed, `YOLO11m` for accuracy
- Save the trained model as `backend/models/head_detector.pt`

## Notes

Normal person detection is not the final solution for crowded exam hall head counting. Use a dedicated head detector for best results.
