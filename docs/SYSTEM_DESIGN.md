# System Design

Camera Feed -> Frame Reader -> Head Detector -> Tracker -> Counter -> WebSocket -> React Dashboard -> SQLite Logs

## Why Head Detection

This project counts visible heads instead of full people because exam hall monitoring is often more accurate when the model focuses on the smaller, partially visible head region. That reduces confusion from desks, chairs, bodies, and occlusion in crowded seating.
