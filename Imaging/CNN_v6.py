import os
import json
import numpy as np
import cv2
import tensorflow as tf
from tensorflow.keras import layers, models
from sklearn.model_selection import train_test_split


# Define dataset structure
home_dir = os.environ['HOME']
dataset_dir = os.path.join(home_dir, "augmented_hbadg")
class_folders = ["pos", "neg"]

img_sz = (224, 224)  # You can adjust this
model_path = os.path.join(home_dir, "test_model.keras")
label_map_path = f"{home_dir}/label_map.json"

# Load dataset
images = []
labels = []

# Process each folder
for class_folder in class_folders:  # Assign 0 to "class_1", 1 to "class_2"
    label = 1 if class_folder == "pos" else 0
    folder_path = os.path.join(dataset_dir, class_folder)

    for image_name in os.listdir(folder_path):
        image_path = os.path.join(folder_path, image_name)
        img = cv2.imread(image_path)
        
        if img is not None:  # Ensure image is readable
            img = cv2.resize(img, img_sz)  # Resize for consistency
            img = img / 255.0  # Normalize pixel values
            images.append(img)
            labels.append(label)  # Assign label based on folder

# Convert lists to NumPy arrays
images = np.array(images, dtype=np.float32)
labels = np.array(labels)

print(f"\n\n\nLoaded {len(images)} images with labels: {set(labels)}")

# Split data
train_images, test_images, train_labels, test_labels = train_test_split(
    images, labels, test_size=0.2, random_state=42
)

print(f"Split data")

def create_model():
    model = models.Sequential([
        layers.Conv2D(16, (16, 16), activation='relu', input_shape=img_sz+(3,)),
        layers.MaxPooling2D((2, 2)),
        layers.Conv2D(8, (9, 9), activation='relu'),
        layers.MaxPooling2D((2, 2)),
        layers.Conv2D(8, (5, 5), activation='relu'),
        layers.GlobalAveragePooling2D(),
        layers.Dense(64, activation='relu'),
        layers.Dense(1, activation='sigmoid')])
 
    model.compile(optimizer='adam', loss='binary_crossentropy', metrics=['accuracy','precision','recall'])
    return model
 
model = create_model()
print("Model Created\n\n\n")

# Train
model.fit(train_images, train_labels, epochs=10, validation_data=(test_images, test_labels))

# Evaluate model
test_loss, test_acc, test_prec, test_rec = model.evaluate(test_images, test_labels)
print(f"Test accuracy: {test_acc:.2f}")

model.save(model_path)
print(f"Model saved to {model_path}")
