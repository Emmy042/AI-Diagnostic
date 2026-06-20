import os
import shutil
import subprocess
import glob
import tensorflow as tf
from tqdm import tqdm
from tensorflow.keras.applications import InceptionV3
from tensorflow.keras.layers import Dense, GlobalAveragePooling2D, Dropout
from tensorflow.keras.models import Model
from tensorflow.keras.preprocessing.image import ImageDataGenerator
from tensorflow.keras.callbacks import ModelCheckpoint, EarlyStopping

# ==========================================
# 1. Configuration & Classes
# ==========================================
CLASS_LABELS = [
    "Melanoma", "Eczema", "Psoriasis", "Acne Vulgaris", 
    "Tinea-Ringworm", "Vitiligo", "Monkeypox"
]

DATASET_PATH = "/content/dataset"
RAW_DATA_PATH = "/content/raw_data"
IMAGE_SIZE = (299, 299)
BATCH_SIZE = 32
EPOCHS = 20

# ==========================================
# 2. Download and Consolidation Logic
# ==========================================
def prepare_datasets():
    """Downloads Kaggle datasets and organizes them into the 7 expected classes."""
    print("Preparing directories...")
    os.makedirs(DATASET_PATH, exist_ok=True)
    for label in CLASS_LABELS:
        os.makedirs(os.path.join(DATASET_PATH, label), exist_ok=True)
        
    print("Downloading datasets from Kaggle...")
    # Requires kaggle API credentials uploaded to Colab!
    
    try:
        # Import kaggle here so it uses the credentials created in __main__
        import kaggle
        kaggle.api.authenticate()
        
        # Dataset 1: Broad skin diseases
        print("Downloading Dataset 1: ismailpromus/skin-diseases-image-dataset...")
        kaggle.api.dataset_download_cli("ismailpromus/skin-diseases-image-dataset", path=f"{RAW_DATA_PATH}/ds1", unzip=True)
        
        # Dataset 2: Contains Monkeypox and other lesions
        print("\nDownloading Dataset 2: ahmedxc4/skin-ds...")
        kaggle.api.dataset_download_cli("ahmedxc4/skin-ds", path=f"{RAW_DATA_PATH}/ds2", unzip=True)
    except Exception as e:
        print("\n[!] Error downloading datasets from Kaggle:", e)
        print("Make sure your API Username and Key are correct and you have accepted any dataset rules.")
        return

    print("Consolidating images into target directories...")
    
    # Map keywords to our exact class labels
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
    
    # Recursively find all images in the raw data folder
    all_images = glob.glob(f"{RAW_DATA_PATH}/**/*.jpg", recursive=True)
    all_images += glob.glob(f"{RAW_DATA_PATH}/**/*.jpeg", recursive=True)
    all_images += glob.glob(f"{RAW_DATA_PATH}/**/*.png", recursive=True)
    
    copied_counts = {label: 0 for label in CLASS_LABELS}
    
    for img_path in tqdm(all_images, desc="Consolidating Images"):
        # Use the parent directory name to determine the class
        parent_dir = os.path.basename(os.path.dirname(img_path)).lower()
        
        # Match keywords
        for keyword, target_class in keyword_map.items():
            if keyword in parent_dir:
                filename = os.path.basename(img_path)
                # Ensure unique filenames if there are collisions
                new_filename = f"{target_class}_{copied_counts[target_class]}_{filename}"
                dest_path = os.path.join(DATASET_PATH, target_class, new_filename)
                
                shutil.copy2(img_path, dest_path)
                copied_counts[target_class] += 1
                break # Only map to the first matching class to avoid duplicates

    print("\nDataset consolidation complete. Image counts per class:")
    for label, count in copied_counts.items():
        print(f" - {label}: {count} images")


# ==========================================
# 3. Model Training
# ==========================================
def train_model():
    print("\nLoading data generators...")
    datagen = ImageDataGenerator(
        preprocessing_function=tf.keras.applications.inception_v3.preprocess_input,
        validation_split=0.2,
        rotation_range=20, 
        width_shift_range=0.2, 
        height_shift_range=0.2, 
        horizontal_flip=True
    )

    train_gen = datagen.flow_from_directory(
        DATASET_PATH, target_size=IMAGE_SIZE, batch_size=BATCH_SIZE, 
        class_mode='categorical', classes=CLASS_LABELS, subset='training'
    )
    val_gen = datagen.flow_from_directory(
        DATASET_PATH, target_size=IMAGE_SIZE, batch_size=BATCH_SIZE, 
        class_mode='categorical', classes=CLASS_LABELS, subset='validation'
    )

    if train_gen.samples == 0:
        print("Error: No training images found. Dataset preparation failed.")
        return

    print("\nBuilding Model Architecture...")
    base_model = InceptionV3(weights='imagenet', include_top=False, input_shape=(299, 299, 3))
    
    # Freeze the base model to preserve pretrained features
    for layer in base_model.layers:
        layer.trainable = False

    x = GlobalAveragePooling2D()(base_model.output)
    x = Dense(512, activation='relu')(x)
    x = Dropout(0.5)(x)
    predictions = Dense(len(CLASS_LABELS), activation='softmax')(x)

    model = Model(inputs=base_model.input, outputs=predictions)
    
    model.compile(optimizer=tf.keras.optimizers.Adam(learning_rate=0.001), 
                  loss='categorical_crossentropy', metrics=['accuracy'])

    # Callbacks to save the best model and stop if it stops improving
    checkpoint = ModelCheckpoint('/content/derma_inceptionv3.keras', monitor='val_accuracy', 
                                 save_best_only=True, mode='max', verbose=1)
    early_stop = EarlyStopping(monitor='val_loss', patience=5, restore_best_weights=True)

    print("\nStarting Training...")
    model.fit(
        train_gen, 
        epochs=EPOCHS, 
        validation_data=val_gen,
        callbacks=[checkpoint, early_stop]
    )

    print("\nTraining Complete! Best model saved as 'derma_inceptionv3.keras'.")
    print("You can download the model from the Colab file explorer.")

if __name__ == "__main__":
    print("=== Colab Dermatology AI Training Script ===")
    
    # Set up Kaggle credentials
    # Kaggle CLI automatically detects KAGGLE_USERNAME and KAGGLE_KEY environment variables
    import getpass
    
    # Set to True if you made a mistake entering your credentials and need to be prompted again.
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
        
        # Write to kaggle.json explicitly because Kaggle CLI prefers the file
        os.makedirs('/root/.kaggle', exist_ok=True)
        with open('/root/.kaggle/kaggle.json', 'w') as f:
            f.write(f'{{"username":"{username}","key":"{key}"}}')
        os.chmod('/root/.kaggle/kaggle.json', 0o600)
        print("Credentials saved securely for this session.\n")
        
    prepare_datasets()
    train_model()
