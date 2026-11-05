import os
from dotenv import load_dotenv

load_dotenv()

DB_CONFIG = {
    "host": os.getenv("DB_HOST"),
    "database": os.getenv("DB_NAME"),
    "user": os.getenv("DB_USER"),
    "password": os.getenv("DB_PASSWORD")
}


import cv2
import psycopg2
from ultralytics import YOLO

VIDEO_PATH = "videos/traffic.mp4"
OUTPUT_PATH = "outputs/vehicle_analytics.mp4"


# Estimate vehicle colour from its image crop
def get_vehicle_color(crop):
    if crop.size == 0:
        return "Unknown"

    b, g, r = [int(x) for x in cv2.mean(crop)[:3]]
    pixel = cv2.cvtColor(
        cv2.resize(crop, (1, 1)),
        cv2.COLOR_BGR2HSV
    )[0, 0]

    h, s, v = [int(x) for x in pixel]

    if v < 50:
        return "Black"
    if s < 35:
        return "White" if v > 190 else "Gray"
    if h < 10 or h >= 170:
        return "Red"
    if h < 25:
        return "Orange"
    if h < 35:
        return "Yellow"
    if h < 85:
        return "Green"
    if h < 130:
        return "Blue"
    return "Other"


# Connect to PostgreSQL
conn = psycopg2.connect(**DB_CONFIG)
cursor = conn.cursor()
print("PostgreSQL connected successfully")

# Load YOLO model
print("Loading YOLO model...")
model = YOLO("yolo11n.pt")

vehicle_classes = [2, 3, 5, 7]
class_names = {
    2: "Car",
    3: "Motorcycle",
    5: "Bus",
    7: "Truck"
}

# Prepare video
cap = cv2.VideoCapture(VIDEO_PATH)

if not cap.isOpened():
    raise SystemExit("Cannot open input video")

fps = cap.get(cv2.CAP_PROP_FPS) or 30
width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
cap.release()

writer = cv2.VideoWriter(
    OUTPUT_PATH,
    cv2.VideoWriter_fourcc(*"mp4v"),
    fps,
    (width, height)
)

line_y = int(height * 0.60)
previous_positions = {}
counted_ids = set()
counts = {"Up": 0, "Down": 0}

print("Starting vehicle analytics...")

results = model.track(
    source=VIDEO_PATH,
    stream=True,
    persist=True,
    tracker="bytetrack.yaml",
    classes=vehicle_classes,
    conf=0.25,
    imgsz=640,
    device="cpu",
    verbose=False
)

frame_count = 0

for result in results:
    frame = result.plot()
    original = result.orig_img

    # Draw counting line
    cv2.line(frame, (0, line_y), (width, line_y),
             (0, 0, 255), 2)

    if result.boxes is not None and result.boxes.id is not None:

        boxes = result.boxes.xyxy.cpu().numpy()
        ids = result.boxes.id.int().cpu().tolist()
        classes = result.boxes.cls.int().cpu().tolist()

        for box, track_id, class_id in zip(boxes, ids, classes):

            x1, y1, x2, y2 = map(int, box)
            center_y = (y1 + y2) // 2

            if track_id in previous_positions and track_id not in counted_ids:

                old_y = previous_positions[track_id]
                direction = None

                if old_y < line_y <= center_y:
                    direction = "Down"
                elif old_y > line_y >= center_y:
                    direction = "Up"

                if direction:
                    crop = original[
                        max(0, y1):min(height, y2),
                        max(0, x1):min(width, x2)
                    ]

                    color = get_vehicle_color(crop)
                    vehicle_type = class_names.get(
                        class_id, "Unknown"
                    )

                    cursor.execute(
                        """
                        INSERT INTO vehicle_events
                        (vehicle_id, vehicle_type, color, direction)
                        VALUES (%s, %s, %s, %s)
                        """,
                        (track_id, vehicle_type, color, direction)
                    )
                    conn.commit()

                    counted_ids.add(track_id)
                    counts[direction] += 1

                    print(
                        f"Saved: ID={track_id}, "
                        f"Type={vehicle_type}, "
                        f"Color={color}, "
                        f"Direction={direction}"
                    )

            previous_positions[track_id] = center_y

    # Display counts
    cv2.putText(
        frame,
        f"Down: {counts['Down']}  Up: {counts['Up']}",
        (20, 40),
        cv2.FONT_HERSHEY_SIMPLEX,
        1, (0, 255, 0), 2
    )

    writer.write(frame)
    frame_count += 1

    if frame_count % 100 == 0:
        print(f"Processed {frame_count} frames")

writer.release()
cursor.close()
conn.close()

print("\n========== VEHICLE ANALYTICS ==========")
print("Down:", counts["Down"])
print("Up:", counts["Up"])
print("Total:", sum(counts.values()))
print("Processed frames:", frame_count)
print("Output:", OUTPUT_PATH)
print("Database connection closed")
