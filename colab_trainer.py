import os
import shutil
import glob
import random
import tensorflow as tf
from tqdm import tqdm
from tensorflow.keras.applications import InceptionV3
from tensorflow.keras.layers import Dense, GlobalAveragePooling2D, Dropout, BatchNormalization
from tensorflow.keras.models import Model
from tensorflow.keras.preprocessing.image import ImageDataGenerator
from tensorflow.keras.callbacks import ModelCheckpoint, EarlyStopping, ReduceLROnPlateau
import numpy as np
from sklearn.utils.class_weight import compute_class_weight
from sklearn.metrics import classification_report, confusion_matrix

# ──────────────────────────────────────────────
# 1. Configuration & Classes
# ──────────────────────────────────────────────
# IMPORTANT: This order MUST match app/diagnostic.py CLASS_LABELS exactly.
# The Flask app uses this same alphabetical-ish ordering when mapping
# argmax indices back to condition names.
CLASS_LABELS = [
    "Melanoma", "Eczema", "Psoriasis", "Acne Vulgaris",
    "Tinea-Ringworm", "Vitiligo", "Monkeypox"
]

DATASET_PATH = "/content/dataset"
RAW_DATA_PATH = "/content/raw_data"
IMAGE_SIZE = (299, 299)
BATCH_SIZE = 32
EPOCHS = 30           # More epochs; EarlyStopping will halt when needed
MAX_PER_CLASS = 2000  # Cap to prevent any single class from dominating


# ──────────────────────────────────────────────
# 2. Download & Consolidation Logic
# ──────────────────────────────────────────────
def prepare_datasets():
    """Downloads Kaggle datasets and organises them into the 7 expected classes."""
    print("Preparing directories...")
    os.makedirs(DATASET_PATH, exist_ok=True)
    for label in CLASS_LABELS:
        os.makedirs(os.path.join(DATASET_PATH, label), exist_ok=True)

    print("Downloading datasets from Kaggle...")

    try:
        import kaggle
        kaggle.api.authenticate()

        # Dataset 1: Broad skin diseases
        print("Downloading Dataset 1: ismailpromus/skin-diseases-image-dataset...")
        kaggle.api.dataset_download_cli(
            "ismailpromus/skin-diseases-image-dataset",
            path=f"{RAW_DATA_PATH}/ds1", unzip=True
        )

        # Dataset 2: Contains Monkeypox and other lesions
        print("\nDownloading Dataset 2: ahmedxc4/skin-ds...")
        kaggle.api.dataset_download_cli(
            "ahmedxc4/skin-ds",
            path=f"{RAW_DATA_PATH}/ds2", unzip=True
        )
    except Exception as e:
        print("\n[!] Error downloading datasets from Kaggle:", e)
        print("Make sure your API Username and Key are correct and "
              "you have accepted any dataset rules.")
        return

    # ── Map source-folder keywords to our target class labels ──
    keyword_map = {
        "melanoma": "Melanoma",
        "eczema": "Eczema",
        "psoriasis": "Psoriasis",
        "acne": "Acne Vulgaris",
        "tinea": "Tinea-Ringworm",
        "ringworm": "Tinea-Ringworm",
        "vitiligo": "Vitiligo",
        "monkeypox": "Monkeypox"
    }

    # Recursively find all images
    all_images = []
    for ext in ("*.jpg", "*.jpeg", "*.png"):
        all_images += glob.glob(f"{RAW_DATA_PATH}/**/{ext}", recursive=True)

    # Group images by target class FIRST so we can cap each class
    class_images: dict[str, list[str]] = {label: [] for label in CLASS_LABELS}

    for img_path in all_images:
        parent_dir = os.path.basename(os.path.dirname(img_path)).lower()
        for keyword, target_class in keyword_map.items():
            if keyword in parent_dir:
                class_images[target_class].append(img_path)
                break

    # ── Balance: cap every class at MAX_PER_CLASS ──
    print(f"\nBalancing classes (max {MAX_PER_CLASS} images per class)...")
    copied_counts = {label: 0 for label in CLASS_LABELS}

    for label, images in class_images.items():
        random.shuffle(images)
        capped = images[:MAX_PER_CLASS]
        for img_path in tqdm(capped, desc=f"  {label}"):
            filename = os.path.basename(img_path)
            new_filename = f"{label}_{copied_counts[label]}_{filename}"
            dest_path = os.path.join(DATASET_PATH, label, new_filename)
            shutil.copy2(img_path, dest_path)
            copied_counts[label] += 1

    print("\nDataset consolidation complete. Image counts per class:")
    for label, count in copied_counts.items():
        print(f"  - {label}: {count} images")

    # ── Warn if any class is drastically underrepresented ──
    counts = list(copied_counts.values())
    if min(counts) == 0:
        print("\n⚠️  WARNING: At least one class has ZERO images. "
              "The model will be unable to learn that class!")
    elif max(counts) / max(min(counts), 1) > 5:
        print("\n⚠️  WARNING: Class ratio exceeds 5:1 even after capping. "
              "Consider sourcing more data for the smaller classes.")


# ──────────────────────────────────────────────
# 3. Model Training (two-phase)
# ──────────────────────────────────────────────
def train_model():
    # ── Stronger augmentation to reduce overfitting on small classes ──
    print("\nLoading data generators...")
    train_datagen = ImageDataGenerator(
        preprocessing_function=tf.keras.applications.inception_v3.preprocess_input,
        validation_split=0.2,
        rotation_range=30,
        width_shift_range=0.2,
        height_shift_range=0.2,
        shear_range=0.15,
        zoom_range=0.2,
        brightness_range=[0.8, 1.2],
        horizontal_flip=True,
        fill_mode="nearest",
    )

    # Validation data should NOT be augmented (only preprocessed)
    val_datagen = ImageDataGenerator(
        preprocessing_function=tf.keras.applications.inception_v3.preprocess_input,
        validation_split=0.2,
    )

    train_gen = train_datagen.flow_from_directory(
        DATASET_PATH, target_size=IMAGE_SIZE, batch_size=BATCH_SIZE,
        class_mode='categorical', classes=CLASS_LABELS,
        subset='training', shuffle=True,
    )
    val_gen = val_datagen.flow_from_directory(
        DATASET_PATH, target_size=IMAGE_SIZE, batch_size=BATCH_SIZE,
        class_mode='categorical', classes=CLASS_LABELS,
        subset='validation', shuffle=False,
    )

    if train_gen.samples == 0:
        print("Error: No training images found. Dataset preparation failed.")
        return

    # Print actual class-index mapping so it can be verified
    print("\nClass index mapping (used by the model):")
    for cls_name, idx in sorted(train_gen.class_indices.items(), key=lambda x: x[1]):
        print(f"  {idx} → {cls_name}")

    # ── Phase 1: Train only the new head (base frozen) ──
    print("\nBuilding Model Architecture...")
    base_model = InceptionV3(weights='imagenet', include_top=False,
                             input_shape=(299, 299, 3))

    for layer in base_model.layers:
        layer.trainable = False

    x = GlobalAveragePooling2D()(base_model.output)
    x = Dense(512, activation='relu')(x)
    x = BatchNormalization()(x)
    x = Dropout(0.5)(x)
    x = Dense(256, activation='relu')(x)
    x = BatchNormalization()(x)
    x = Dropout(0.3)(x)
    predictions = Dense(len(CLASS_LABELS), activation='softmax')(x)

    model = Model(inputs=base_model.input, outputs=predictions)

    model.compile(
        optimizer=tf.keras.optimizers.Adam(learning_rate=1e-3),
        loss='categorical_crossentropy',
        metrics=['accuracy'],
    )

    # ── Class weights ──
    print("\nComputing Class Weights to handle dataset imbalance...")
    class_weights_array = compute_class_weight(
        class_weight='balanced',
        classes=np.unique(train_gen.classes),
        y=train_gen.classes
    )
    class_weights = dict(enumerate(class_weights_array))
    print("Class Weights:", class_weights)

    callbacks = [
        ModelCheckpoint('/content/derma_inceptionv3.keras',
                        monitor='val_accuracy', save_best_only=True,
                        mode='max', verbose=1),
        EarlyStopping(monitor='val_loss', patience=5,
                      restore_best_weights=True),
        ReduceLROnPlateau(monitor='val_loss', factor=0.5, patience=3,
                          min_lr=1e-6, verbose=1),
    ]

    print("\n── Phase 1: Training classification head (base frozen) ──")
    model.fit(
        train_gen,
        epochs=10,
        validation_data=val_gen,
        callbacks=callbacks,
        class_weight=class_weights,
    )

    # ── Phase 2: Fine-tune the top InceptionV3 layers ──
    print("\n── Phase 2: Fine-tuning top InceptionV3 layers ──")
    for layer in base_model.layers[-30:]:
        layer.trainable = True

    model.compile(
        optimizer=tf.keras.optimizers.Adam(learning_rate=1e-5),
        loss='categorical_crossentropy',
        metrics=['accuracy'],
    )

    model.fit(
        train_gen,
        epochs=EPOCHS,
        initial_epoch=10,
        validation_data=val_gen,
        callbacks=callbacks,
        class_weight=class_weights,
    )

    print("\nTraining Complete! Best model saved as 'derma_inceptionv3.keras'.")

    # ── Post-training bias check ──
    _validate_model(model, val_gen)


# ──────────────────────────────────────────────
# 4. Post-Training Validation
# ──────────────────────────────────────────────
def _validate_model(model, val_gen):
    """Run a quick classification report to catch single-class bias
    BEFORE you download the model."""
    print("\n══════════════════════════════════════")
    print("  POST-TRAINING BIAS CHECK")
    print("══════════════════════════════════════")

    val_gen.reset()
    preds = model.predict(val_gen, verbose=1)
    pred_classes = np.argmax(preds, axis=1)
    true_classes = val_gen.classes[:len(pred_classes)]

    # Per-class precision / recall / f1
    report = classification_report(
        true_classes, pred_classes,
        target_names=CLASS_LABELS, zero_division=0
    )
    print("\nClassification Report:\n")
    print(report)

    # Quick sanity: flag if one class captures > 50 % of all predictions
    unique, counts = np.unique(pred_classes, return_counts=True)
    total = counts.sum()
    for cls_idx, cnt in zip(unique, counts):
        pct = cnt / total * 100
        if pct > 50:
            print(f"\n⚠️  WARNING: Class '{CLASS_LABELS[cls_idx]}' received "
                  f"{pct:.1f}% of ALL predictions — the model is biased!")
            print("   Consider adding more data for underrepresented classes "
                  "or adjusting class weights.\n")

    print("You can download the model from the Colab file explorer.")


# ──────────────────────────────────────────────
# 5. Entry Point (Colab / CLI)
# ──────────────────────────────────────────────
if __name__ == "__main__":
    print("=== Colab Dermatology AI Training Script ===")

    # ── Kaggle credentials ──
    import getpass

    # Set to True if you made a mistake entering credentials and need to re-enter.
    RESET_CREDENTIALS = True

    if RESET_CREDENTIALS:
        if os.path.exists('/root/.kaggle/kaggle.json'):
            os.remove('/root/.kaggle/kaggle.json')
        if 'KAGGLE_USERNAME' in os.environ:
            del os.environ['KAGGLE_USERNAME']
        if 'KAGGLE_KEY' in os.environ:
            del os.environ['KAGGLE_KEY']

    if os.path.exists('kaggle.json'):
        os.makedirs('/root/.kaggle', exist_ok=True)
        shutil.copy2('kaggle.json', '/root/.kaggle/kaggle.json')
        os.chmod('/root/.kaggle/kaggle.json', 0o600)
    elif not os.path.exists('/root/.kaggle/kaggle.json'):
        print("\n--- Kaggle API Authentication ---")
        print("Since you have the raw API key, please paste it here.")
        username = input("Enter your Kaggle Username: ").strip()
        key = getpass.getpass("Enter your Kaggle API Key (input will be hidden): ").strip()

        os.makedirs('/root/.kaggle', exist_ok=True)
        with open('/root/.kaggle/kaggle.json', 'w') as f:
            f.write(f'{{"username":"{username}","key":"{key}"}}')
        os.chmod('/root/.kaggle/kaggle.json', 0o600)
        print("Credentials saved securely for this session.\n")

    prepare_datasets()
    train_model()
