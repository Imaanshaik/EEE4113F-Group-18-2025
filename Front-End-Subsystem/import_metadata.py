import sqlite3
import os
import json

DB_PATH = "data/detections.db"
METADATA_DIR = "static/data/metadata/"

# Connect to database
conn = sqlite3.connect(DB_PATH)
c = conn.cursor()

inserted = 0

# Loop through each metadata file
for filename in os.listdir(METADATA_DIR):
    if filename.endswith(".json"):
        filepath = os.path.join(METADATA_DIR, filename)
        with open(filepath, "r") as f:
            data = json.load(f)

        # Insert into database
        c.execute("""
            INSERT INTO detections (timestamp, animal_name, confidence, image_filename, video_filename)
            VALUES (?, ?, ?, ?, ?)
        """, (
            data["timestamp"],
            data["animal_name"],
            data["confidence"],
            data["image_filename"],
            data["video_filename"]
        ))

        inserted += 1
        os.remove(filepath)  # Delete metadata file after importing

conn.commit()
conn.close()

print(f"✅ Imported {inserted} detection(s) from metadata.")
