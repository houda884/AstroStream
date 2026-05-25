from ultralytics import YOLO

model = YOLO("yolov8n.pt")
MIN_CONFIDENCE = 0.5

def detect_objects(frame):
    results = model(frame, verbose=False)
    detections = []

    for r in results:
        for box in r.boxes:
            x1, y1, x2, y2 = box.xyxy[0].tolist()
            conf = float(box.conf[0])
            cls = int(box.cls[0])
            label = model.names[cls]

            if conf < MIN_CONFIDENCE:
                continue

            detections.append({
                "label": label,
                "confidence": round(conf, 2),
                "x": int(x1),
                "y": int(y1),
                "w": int(x2 - x1),
                "h": int(y2 - y1)
            })

    return detections