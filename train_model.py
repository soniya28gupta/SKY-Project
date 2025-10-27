import tensorflow as tf
from tensorflow.keras.models import Sequential
from tensorflow.keras import layers
import json
import os
import matplotlib.pyplot as plt

# =============================================================================
# 1. DEFINE PATHS AND CONSTANTS
# =============================================================================
# IMPORTANT: This path must point to your dataset folder
base_dir = r"C:\Users\soniy\Downloads\SKY"
train_dir = os.path.join(base_dir, 'train')
test_dir = os.path.join(base_dir, 'test') # Make sure this folder also has the same class subfolders

# Model constants
IMG_SIZE = 224
BATCH_SIZE = 32

# =============================================================================
# 2. LOAD DATASETS
# =============================================================================
# Load training and validation datasets
# This will fail if the 'train' directory is not correctly structured with class subfolders
train_ds = tf.keras.utils.image_dataset_from_directory(
    train_dir,
    validation_split=0.2,
    subset="training",
    seed=123,
    image_size=(IMG_SIZE, IMG_SIZE),
    batch_size=BATCH_SIZE,
)

val_ds = tf.keras.utils.image_dataset_from_directory(
    train_dir,
    validation_split=0.2,
    subset="validation",
    seed=123,
    image_size=(IMG_SIZE, IMG_SIZE),
    batch_size=BATCH_SIZE,
)

# =============================================================================
# 3. CREATE 'class_names.json'
# =============================================================================
class_names = train_ds.class_names
NUM_CLASSES = len(class_names)

# Check if you have more than one class
if NUM_CLASSES <= 1:
    print(f"❌ Error: Found only {NUM_CLASSES} class. A classifier needs at least 2. Please fix your 'train' folder structure.")
    exit() # Stop the script if there's only one class

print(f"✅ Found {NUM_CLASSES} classes: {class_names}")
with open('class_names.json', 'w') as f:
    json.dump(class_names, f)
print("✅ class_names.json file created!")

# Configure datasets for performance
AUTOTUNE = tf.data.AUTOTUNE
train_ds = train_ds.cache().shuffle(1000).prefetch(buffer_size=AUTOTUNE)
val_ds = val_ds.cache().prefetch(buffer_size=AUTOTUNE)

# =============================================================================
# 4. BUILD THE MODEL (This replaces the '[...]' placeholder)
# =============================================================================
# Data Augmentation Layer
data_augmentation = Sequential([
    layers.RandomFlip("horizontal_and_vertical"),
    layers.RandomRotation(0.2),
], name="data_augmentation")

# Base Model (MobileNetV2)
base_model = tf.keras.applications.MobileNetV2(input_shape=(IMG_SIZE, IMG_SIZE, 3),
                                               include_top=False,
                                               weights='imagenet')
base_model.trainable = False

# Assemble the full model
model = Sequential([
    layers.Input(shape=(IMG_SIZE, IMG_SIZE, 3)),
    data_augmentation,
    layers.Lambda(tf.keras.applications.mobilenet_v2.preprocess_input),
    base_model,
    layers.GlobalAveragePooling2D(),
    layers.Dropout(0.2),
    layers.Dense(NUM_CLASSES, activation='softmax')
])

# =============================================================================
# 5. COMPILE AND TRAIN THE MODEL
# =============================================================================
model.compile(optimizer='adam',
              loss=tf.keras.losses.SparseCategoricalCrossentropy(),
              metrics=['accuracy'])

model.summary()

print("\n--- Starting Model Training ---")
history = model.fit(train_ds, validation_data=val_ds, epochs=10)
print("--- Model Training Finished ---")


# =============================================================================
# 6. SAVE THE FINAL MODEL
# =============================================================================
model.save('plant_disease_model.keras')
print("✅ plant_disease_model.keras file created!")