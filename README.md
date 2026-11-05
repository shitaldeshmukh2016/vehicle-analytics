
# Vehicle Analytics Dashboard

A real-time vehicle analytics system that detects and tracks vehicles, estimates their colours, identifies line-crossing direction, stores detection events in PostgreSQL, and displays analytics through a React dashboard.

## Features

- Vehicle detection using YOLO
- Vehicle tracking using ByteTrack
- Vehicle type identification
- Basic vehicle colour estimation using OpenCV
- Vehicle direction detection using a virtual counting line
- Detection event storage in PostgreSQL
- Flask REST API
- React dashboard with automatic refresh every 5 seconds
- Recent vehicle event history

## Technology Stack

| Component | Technology |
|---|---|
| Programming Language | Python |
| Vehicle Detection | YOLO (Ultralytics) |
| Object Tracking | ByteTrack |
| Image Processing | OpenCV |
| Backend | Flask |
| Database | PostgreSQL |
| Frontend | React.js |
| Frontend Tools | Node.js, Vite |
| API | REST API |
| Version Control | Git |

## Project Structure

```text
vehicle-analytics/
│
├── videos/
│   └── traffic.mp4
│
├── outputs/
│   ├── vehicle_detection.mp4
│   └── vehicle_analytics.mp4
│
├── frontend/
│   ├── src/
│   │   ├── App.jsx
│   │   └── App.css
│   └── package.json
│
├── .venv/
├── vehicle_detection.py
├── vehicle_analytics.py
├── app.py
└── README.md
```

## Prerequisites

- Python 3.12
- Node.js and npm
- PostgreSQL
- Ubuntu / Linux environment
- Git

## Installation

### 1. Clone the repository

```bash
git clone YOUR_GITHUB_REPOSITORY_URL
cd vehicle-analytics
```

### 2. Create Python virtual environment

```bash
python3 -m venv .venv
source .venv/bin/activate
```

### 3. Install Python dependencies

```bash
pip install ultralytics opencv-python psycopg2-binary flask flask-cors
```

### 4. Configure PostgreSQL

Create a database named:

```sql
CREATE DATABASE vehicle_analytics;
```

Create the database table:

```sql
CREATE TABLE vehicle_events (
    id SERIAL PRIMARY KEY,
    vehicle_id INTEGER NOT NULL,
    vehicle_type VARCHAR(50),
    color VARCHAR(30),
    direction VARCHAR(20),
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

Configure your PostgreSQL username, password, and database details in `app.py` and `vehicle_analytics.py`.

### 5. Install frontend dependencies

```bash
cd frontend
npm install
```

## Running the Project

Start PostgreSQL:

```bash
sudo service postgresql start
```

Start the Flask backend from the project root:

```bash
source .venv/bin/activate
python app.py
```

Backend URL:

```text
http://localhost:5000
```

Start the React frontend in another terminal:

```bash
cd frontend
npm run dev
```

Frontend URL:

```text
http://localhost:5173
```

Run vehicle analytics in another terminal:

```bash
cd ~/vehicle-analytics
source .venv/bin/activate
python vehicle_analytics.py
```

## API Endpoints

| Endpoint | Description |
|---|---|
| GET / | Backend status |
| GET /api/stats | Vehicle statistics and colour counts |
| GET /api/events | Recent vehicle detection events |

## Dashboard

The dashboard displays:

- Total detected vehicles
- Up and down direction counts
- Vehicle colour analysis
- Recent vehicle detection events

The dashboard automatically refreshes every 5 seconds.

## Current Implementation Notes

- Vehicle detection and tracking are implemented using YOLO and ByteTrack.
- Colour identification currently uses an OpenCV-based HSV heuristic.
- Line crossing is implemented using vehicle tracking coordinates.
- MediaMTX RTSP integration and NVIDIA DeepStream integration are not yet implemented in this version.
- This implementation is a functional computer-vision alternative, not a DeepStream-based implementation.

## Future Improvements

- Integrate MediaMTX for RTSP stream ingestion.
- Implement NVIDIA DeepStream inference pipeline.
- Add a trained secondary vehicle colour classifier.
- Improve vehicle counting and tracking accuracy.
- Add real-time camera stream visualization.

## Author

Vehicle Analytics Dashboard - Computer Vision Project
