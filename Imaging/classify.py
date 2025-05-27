import tensorflow as tf
from tensorflow.keras import layers, models
import numpy as np
import cv2
import os
from glob import glob
from sklearn.model_selection import train_test_split
import json

home_dir = os.environ['HOME']
img_sz = (224, 224)  # You can adjust this
model_path = os.path.join(home_dir, "test_model.keras")

# Classification function
def classify_image(image_path, model_path):
    model = tf.keras.models.load_model(model_path)
    img = cv2.imread(image_path)
    img = cv2.resize(img, img_sz)  
    img = img / 255.0  
    img = np.expand_dims(img, axis=0)  
 
    predictions = model.predict(img)
    predicted_class = np.argmax(predictions)

    threshold = 0.5
    if predictions[predicted_class] > threshold:
        guess = "Honey Badger"
    else:
        guess = "Other"

    return guess, predictions[predicted_class]
    #class_names = ["Other","Honey Badger"]
    #return class_names[predicted_class],predictions[predicted_class]


num_cam_imgs = 5
for i in range(num_cam_imgs):
    image_path = os.path.join(home_dir, f"cam_test_{i+1}.jpg")
    class_guess, confidence = classify_image(image_path, model_path)
    print(f"Guess {i+1}: {class_guess}\nConfidence: {confidence}")
