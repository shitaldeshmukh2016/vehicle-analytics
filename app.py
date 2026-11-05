import os
from dotenv import load_dotenv

load_dotenv()

DB_CONFIG = {
    "host": os.getenv("DB_HOST"),
    "database": os.getenv("DB_NAME"),
    "user": os.getenv("DB_USER"),
    "password": os.getenv("DB_PASSWORD")
}





from flask import Flask, jsonify
from flask_cors import CORS
import psycopg2
from psycopg2.extras import RealDictCursor

app = Flask(__name__)
CORS(app)



def get_connection():
    return psycopg2.connect(**DB_CONFIG)


@app.route("/")
def home():
    return jsonify({"message": "Vehicle Analytics API is running"})


@app.route("/api/stats")
def stats():
    conn = get_connection()
    cur = conn.cursor(cursor_factory=RealDictCursor)

    cur.execute("""
        SELECT
            COUNT(*) AS total,
            COUNT(*) FILTER (WHERE direction = 'Up') AS up,
            COUNT(*) FILTER (WHERE direction = 'Down') AS down
        FROM vehicle_events
    """)
    result = cur.fetchone()

    cur.execute("""
        SELECT color, COUNT(*) AS count
        FROM vehicle_events
        GROUP BY color
        ORDER BY count DESC
    """)
    colors = cur.fetchall()

    cur.close()
    conn.close()

    return jsonify({
        "total": result["total"],
        "up": result["up"],
        "down": result["down"],
        "colors": colors
    })


@app.route("/api/events")
def events():
    conn = get_connection()
    cur = conn.cursor(cursor_factory=RealDictCursor)

    cur.execute("""
        SELECT id, vehicle_id, vehicle_type, color,
               direction, timestamp
        FROM vehicle_events
        ORDER BY timestamp DESC
        LIMIT 20
    """)

    rows = cur.fetchall()
    cur.close()
    conn.close()

    for row in rows:
        row["timestamp"] = row["timestamp"].isoformat()

    return jsonify(rows)


if __name__ == "__main__":
    app.run(debug=True, port=5000)
