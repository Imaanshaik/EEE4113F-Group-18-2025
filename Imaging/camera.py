import os
from datetime import datetime, timedelta
from time import sleep

import json
from gpiozero import Button, DigitalOutputDevice
from picamzero import PiCam

# Initialize GPIO for trigger and IR LED driver MOSFETs
trigger = Button(15)
led1 = DigitalOutputDevice(12)
led2 = DigitalOutputDevice(16)

# Directory
home_dir = os.environ['HOME']
detect_dir = f"{home_dir}/Desktop/detections"

# Initialize the PiCam
camera = PiCam()

def capture(rec_time):
    timestamp = datetime.now()
    suffix = timestamp.strftime('%Y%m%d%H%M%S')
    filename = f"{detect_dir}/detection_{suffix}"
    
    print("Trigger sent, starting capture...")

    # Turn on MOSFETs
    led1.on()
    led2.on()

    # Take image
    camera.capture(f"{filename}.jpg")
    print(f"Image saved: {filename}.jpg")

    # Take video
    camera.record_video(f"{filename}.mp4", duration=rec_time)
    print(f"Video saved: {filename}.mp4")

    # Turn off outputs
    led1.off()
    led2.off()

    print("Capture complete, processing...")
    return timestamp,filename

def writeJSON(timestamp,filename, animal,confidence):    
    # Create JSON data
    json_data = {
        "timestamp": timestamp.strftime('%Y-%m-%d %H:%M:%S'),
        "flag": animal,
        "flag2": round(confidence, 2),
        "image_filename": f"{filename}.jpg",
        "video_filename": f"{filename}.mp4"
    }

    # Write JSON file
    json_filename = f"{filename}.json"
    with open(json_filename, "w") as json_file:
        json.dump(json_data, json_file, indent=4)

    print(f"JSON file created: {json_filename}")
    print(f"Waiting for next trigger")

def detect(timestamp,filename):
    with open(f"{filename}.jpg", "rb") as jpg_file:
        # some processing stuff
        animal = "TEST"
        confidence = 0.999999
        print(f"Animal detected: {animal}\nConfidence: {round(confidence, 2)}")
    return animal,confidence


# Wait for button press indefinitely
dead_time = 15
rec_time = deadtime
timestamp = datetime.now() - timedelta(seconds=dead_time)
while True:
    trigger.wait_for_press()
    if datetime.now() > timestamp + timedelta(seconds=dead_time):
        timestamp,filename = capture(rec_time)
        sleep(3)
        animal,confidence = detect(timestamp,filename)
        writeJSON(timestamp,filename, animal,confidence)
