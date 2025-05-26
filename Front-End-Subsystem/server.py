from flask import Flask, render_template, request, redirect, url_for, flash
import sys
import sqlite3
from collections import Counter
from datetime import datetime, timedelta

app = Flask(__name__)
app.secret_key = 'super_secret_key'  # Needed for flashing messages

CORRECT_PASSWORD = "penguin123"

@app.route('/', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        entered_pw = request.form.get('password')
        if entered_pw == CORRECT_PASSWORD:
            return redirect(url_for('dashboard'))
        else:
            flash("Incorrect password. Try again.")
            return redirect(url_for('login'))
    return render_template('index.html')


@app.route('/dashboard')
def dashboard():
    now = datetime.now()
    one_day_ago = now - timedelta(hours=24)
    one_week_ago = now - timedelta(days=7)

    conn = sqlite3.connect("data/detections.db")
    c = conn.cursor()
    c.execute("SELECT timestamp, animal_name FROM detections ORDER BY timestamp DESC")
    rows = c.fetchall()

    # Get last 5 full entries
    c.execute("SELECT timestamp, animal_name, image_filename, video_filename FROM detections ORDER BY timestamp DESC LIMIT 5")
    recent_rows = c.fetchall()
    conn.close()

    timestamps = [datetime.fromisoformat(r[0].strip().split('.')[0]) for r in rows]
    animals = [r[1] for r in rows]
    data = list(zip(timestamps, animals))

    count_24h = sum(1 for ts, _ in data if ts >= one_day_ago)
    most_common_animal = Counter(animals).most_common(1)[0][0] if animals else "N/A"
    last_detected = timestamps[0].strftime("%Y-%m-%d %H:%M:%S") if timestamps else "No data"

    return render_template("dashboard.html",
                           count_24h=count_24h,
                           most_common=most_common_animal,
                           last=last_detected,
                           pie_labels=list(Counter(a for ts, a in data if ts >= one_week_ago).keys()),
                           pie_data=list(Counter(a for ts, a in data if ts >= one_week_ago).values()),
                           recent=recent_rows)


@app.route('/animal-log')
def animal_log():
    sort_order = request.args.get("sort", "desc")  # default: newest first
    filter_animal = request.args.get("animal", "All")

    conn = sqlite3.connect("data/detections.db")
    c = conn.cursor()

    query = "SELECT timestamp, animal_name, confidence, image_filename, video_filename FROM detections"
    params = []

    if filter_animal != "All":
        query += " WHERE animal_name = ?"
        params.append(filter_animal)

    if sort_order == "asc":
        query += " ORDER BY timestamp ASC"
    else:
        query += " ORDER BY timestamp DESC"

    c.execute(query, params)
    detections = c.fetchall()
    conn.close()

    detection_list = [
        {
            "timestamp": row[0],
            "animal": row[1],
            "confidence": f"{row[2] * 100:.0f}%",
            "image": row[3],
            "video": row[4]
        }
        for row in detections
    ]

    return render_template("animal_log.html", detections=detection_list, current_sort=sort_order, current_filter=filter_animal)


@app.route('/analytics')
def analytics():
    time_range = request.args.get("range", "7d")
    now = datetime.now()

    if time_range == "24h":
        cutoff = now - timedelta(hours=24)
    elif time_range == "30d":
        cutoff = now - timedelta(days=30)
    else:
        cutoff = now - timedelta(days=7)

    conn = sqlite3.connect("data/detections.db")
    c = conn.cursor()
    c.execute("""
        SELECT timestamp, animal_name FROM detections
        WHERE timestamp >= ?
    """, (cutoff.strftime("%Y-%m-%d %H:%M:%S"),))
    rows = c.fetchall()
    conn.close()

    timestamps = [datetime.fromisoformat(r[0].strip().split('.')[0]) for r in rows]
    animals = [r[1] for r in rows]

    animal_counts = Counter(animals)
    bar_labels = list(animal_counts.keys())
    bar_data = [animal_counts[a] for a in bar_labels]

    date_buckets = Counter(ts.date() for ts in timestamps)
    sorted_days = sorted(date_buckets.keys())
    line_labels = [d.strftime("%b %d") for d in sorted_days]
    line_data = [date_buckets[d] for d in sorted_days]

    bucket_ranges = [(h, h+1) for h in range(24)]
    bucket_labels = [f"{h:02d}:00–{(h+1)%24:02d}:00" for h in range(24)]
    animal_names = sorted(set(animals))

    matrix_data = []
    by_animal_hour = {animal: [0]*24 for animal in animal_names}

    for a, ts in zip(animals, timestamps):
        bucket_index = ts.hour  # 0–23
        by_animal_hour[a][bucket_index] += 1

    for y, animal in enumerate(animal_names):
        for x, count in enumerate(by_animal_hour[animal]):
            matrix_data.append({"x": x, "y": y, "v": count})


    return render_template("analytics.html",
        bar_labels=bar_labels,
        bar_data=bar_data,
        line_labels=line_labels,
        line_data=line_data,
        selected_range=time_range,
        matrix_data=matrix_data,
        bucket_labels=bucket_labels,
        animal_labels=animal_names
    )



if __name__ == "__main__":
    port = 8000
    try:
        app.run(host="0.0.0.0", port=port)
    except OSError as e:
        if e.errno == 98:
            print(f"Error: Port {port} is already in use.")
        else:
            print(f"Error: {str(e)}")
        sys.exit(1)
    except ValueError:
        print(f"Error: Invalid port number {port}. Port must be an integer between 0 and 65535.")
        sys.exit(1)
    except PermissionError:
        print(f"Error: You do not have permission to use port {port}. Try using a port above 1024.")
        sys.exit(1)
    except Exception as e:
        print(f"Unexpected error: {str(e)}")
        sys.exit(1)
