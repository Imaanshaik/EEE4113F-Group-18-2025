import sqlite3

conn = sqlite3.connect("data/detections.db")
c = conn.cursor()
c.execute("SELECT COUNT(*) FROM detections")
count = c.fetchone()[0]
print(f"Number of records in database: {count}")
conn.close()
