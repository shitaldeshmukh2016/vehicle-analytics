import cv2
import os
from collections import defaultdict
from ultralytics import YOLO

# Project paths
VIDEO_PATH = "videos/traffic.mp4"
OUTPUT_DIR = "outputs"
OUTPUT_VIDEO = os.path.join(OUTPUT_DIR, "vehicle_detection.mp4")

os.makedirs(OUTPUT_DIR, exist_ok=True)

# Vehicle classes in the COCO dataset
VEHICLE_CLASSES = [2, 3, 5, 7]
CLASS_NAMES = {
    2: "Car",
    3: "Motorcycle",
    5: "Bus",
    7: "Truck"
}

print("Loading YOLO model...")
model = YOLO("yolo11n.pt")

# Store unique tracked vehicle IDs
tracked_vehicles = defaultdict(set)

video = cv2.VideoCapture(VIDEO_PATH)

if not video.isOpened():
    raise SystemExit(f"Cannot open video: {VIDEO_PATH}")

fps = video.get(cv2.CAP_PROP_FPS)
width = int(video.get(cv2.CAP_PROP_FRAME_WIDTH))
height = int(video.get(cv2.CAP_PROP_FRAME_HEIGHT))

if fps <= 0:
    fps = 30

writer = cv2.VideoWriter(
    OUTPUT_VIDEO,
    cv2.VideoWriter_fourcc(*"mp4v"),
    fps,
    (width, height)
)

video.release()

print("Starting vehicle detection and tracking...")

results = model.track(
    source=VIDEO_PATH,
    stream=True,
    persist=True,
    tracker="bytetrack.yaml",
    classes=VEHICLE_CLASSES,
    conf=0.25,
    imgsz=640,
    device="cpu",
    verbose=False
)

frame_count = 0

for result in results:
    frame = result.plot()

    if result.boxes is not None and result.boxes.id is not None:
        track_ids = result.boxes.id.int().cpu().tolist()
        class_ids = result.boxes.cls.int().cpu().tolist()

        for track_id, class_id in zip(track_ids, class_ids):
            tracked_vehicles[class_id].add(track_id)

    # Display unique vehicle counts
    y = 35
    for class_id, name in CLASS_NAMES.items():
        count = len(tracked_vehicles[class_id])
        cv2.putText(
            frame,
            f"{name}: {count}",
            (20, y),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.8,
            (0, 255, 0),
            2
        )
        y += 35

    total = sum(len(ids) for ids in tracked_vehicles.values())

    cv2.putText(
        frame,
        f"Total Vehicles: {total}",
        (20, y + 10),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.9,
        (0, 255, 255),
        2
    )

    writer.write(frame)
    frame_count += 1

    if frame_count % 100 == 0:
        print(f"Processed {frame_count} frames")

writer.release()

print("\n========== VEHICLE ANALYTICS REPORT ==========")

for class_id, name in CLASS_NAMES.items():
    print(f"{name}: {len(tracked_vehicles[class_id])}")

total = sum(len(ids) for ids in tracked_vehicles.values())
print(f"Total Unique Vehicles: {total}")

print(f"\nProcessed frames: {frame_count}")
print(f"Output saved at: {OUTPUT_VIDEO}")
print("Processing completed!")