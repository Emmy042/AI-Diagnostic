import os
os.environ["TF_CPP_MIN_LOG_LEVEL"] = "2"

import tensorflow as tf
from tensorflow.keras.applications import InceptionV3
from tensorflow.keras.layers import Dense, GlobalAveragePooling2D, Dropout
from tensorflow.keras.models import Model
from tensorflow.keras.preprocessing.image import ImageDataGenerator

# ==========================================
# 1. Configuration
# ==========================================
# Make sure this matches the exact order in your web app's app/diagnostic.py!
CLASS_LABELS = [
    "Melanoma",
    "Eczema",
    "Psoriasis",
    "Acne Vulgaris",
    "Tinea-Ringworm", # Avoid slashes in folder names
    "Vitiligo",
    "Monkeypox",
]

# Path to your dataset folder. 
# Inside "dataset/", there should be 7 folders named exactly like the labels above.
DATASET_PATH = "dataset/" 
IMAGE_SIZE = (299, 299)
BATCH_SIZE = 32
EPOCHS = 10

def main():
    if not os.path.exists(DATASET_PATH):
        print(f"Error: Could not find dataset folder '{DATASET_PATH}'")
        print("Please create a 'dataset' folder and place your images in subfolders named after each skin condition.")
        return

    # ==========================================
    # 2. Data Loading & Augmentation
    # ==========================================
    # We use ImageDataGenerator to load images and automatically augment them 
    # (flip, rotate, zoom) to help the model learn better.
    # InceptionV3 requires inputs to be scaled between -1 and 1.
    datagen = ImageDataGenerator(
        preprocessing_function=tf.keras.applications.inception_v3.preprocess_input,
        validation_split=0.2, # 20% of images used for validation
        rotation_range=20,
        width_shift_range=0.2,
        height_shift_range=0.2,
        horizontal_flip=True
    )

    print("Loading training data...")
    train_generator = datagen.flow_from_directory(
        DATASET_PATH,
        target_size=IMAGE_SIZE,
        batch_size=BATCH_SIZE,
        class_mode='categorical',
        classes=CLASS_LABELS,
        subset='training'
    )

    print("Loading validation data...")
    val_generator = datagen.flow_from_directory(
        DATASET_PATH,
        target_size=IMAGE_SIZE,
        batch_size=BATCH_SIZE,
        class_mode='categorical',
        classes=CLASS_LABELS,
        subset='validation'
    )

    if train_generator.samples == 0:
        print("No images found! Make sure you placed images inside the condition subfolders.")
        return

    # ==========================================
    # 3. Model Architecture (InceptionV3)
    # ==========================================
    print("Building model...")
    # Load base InceptionV3 model, excluding the top classification layer
    base_model = InceptionV3(weights='imagenet', include_top=False, input_shape=(299, 299, 3))
    
    # Freeze the base model layers so we don't destroy the pre-trained weights
    for layer in base_model.layers:
        layer.trainable = False

    # Add our own custom layers on top for the 7 skin conditions
    x = base_model.output
    x = GlobalAveragePooling2D()(x)
    x = Dense(512, activation='relu')(x)
    x = Dropout(0.5)(x) # Helps prevent overfitting
    predictions = Dense(len(CLASS_LABELS), activation='softmax')(x)

    model = Model(inputs=base_model.input, outputs=predictions)

    model.compile(
        optimizer=tf.keras.optimizers.Adam(learning_rate=0.001),
        loss='categorical_crossentropy',
        metrics=['accuracy']
    )

    # ==========================================
    # 4. Train the Model
    # ==========================================
    print("Starting training...")
    model.fit(
        train_generator,
        epochs=EPOCHS,
        validation_data=val_generator
    )

    # ==========================================
    # 5. Save the Model
    # ==========================================
    model.save("derma_inceptionv3.keras")
    print("\nModel saved successfully as 'derma_inceptionv3.keras'!")
    print("You can now restart your Flask app to use the new model.")

if __name__ == "__main__":
    main()
