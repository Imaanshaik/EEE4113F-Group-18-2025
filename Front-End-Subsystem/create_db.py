import sqlite3
import os

# Ensure the data folder exists
os.makedirs("data", exist_ok=True)

# Connect to (or create) the database
conn = sqlite3.connect("data/detections.db")
c = conn.cursor()

# Create the detections table
c.execute("""
CREATE TABLE IF NOT EXISTS detections (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    timestamp TEXT NOT NULL,
    animal_name TEXT NOT NULL,
    confidence REAL NOT NULL,
    image_filename TEXT NOT NULL,
    video_filename TEXT NOT NULL
);
""")

conn.commit()
conn.close()

print("Database and table created successfully.")
