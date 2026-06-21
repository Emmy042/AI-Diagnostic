# AI Dermatology Diagnostic Support

A Flask-based web application that uses a trained InceptionV3 deep learning model to assist in diagnosing skin conditions from uploaded images. Built as a school project based on Chapter 3 of the AI dermatology diagnostic system document.

## What It Does

- Upload a skin image through a browser interface.
- Validates JPG, PNG, and WEBP files (up to 8 MB).
- Preprocesses images for InceptionV3 (299×299, normalized to [-1, 1]).
- Returns a predicted condition, confidence score, clinical note, and referral recommendation.
- Asynchronous inference with a processing/status polling UI.
- Supports a demo mode (hash-based) when no trained model is available.
- Keeps uploads/results out of persistent storage for privacy.

## Supported Conditions

| Condition | Description |
|---|---|
| Melanoma | Potentially serious skin cancer requiring prompt assessment |
| Eczema | Inflammatory condition with itching, dryness, and flares |
| Psoriasis | Chronic inflammatory condition producing scaly plaques |
| Acne Vulgaris | Blocked follicles with inflammation, papules, or nodules |
| Tinea/Ringworm | Fungal infection with itchy, ring-shaped patches |
| Vitiligo | Pigmentary disorder causing depigmented patches |
| Monkeypox | Viral illness with fever and characteristic skin lesions |

## Prerequisites

- **Python 3.12** (TensorFlow does not yet support Python 3.13+)
- A trained model file: `derma_inceptionv3.keras` (not included in the repo — see [Training the Model](#training-the-model))

## Setup

```powershell
# Create a virtual environment with Python 3.12
py -3.12 -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

## Configuration

Create a `.env` file in the project root:

```env
DERMA_DEMO_MODE=False
DERMA_MODEL_PATH=derma_inceptionv3.keras
```

| Variable | Default | Description |
|---|---|---|
| `DERMA_MODEL_PATH` | `derma_inceptionv3.keras` | Path to the trained Keras model |
| `DERMA_DEMO_MODE` | `False` | Set to `True` to run without a real model |
| `MAX_UPLOAD_MB` | `8` | Maximum upload size in megabytes |
| `FLASK_DEBUG` | `0` | Set to `1` for debug mode |

## Run Locally

```powershell
python run.py
```

Open: [http://127.0.0.1:5000](http://127.0.0.1:5000)

### Demo Mode (no model required)

If you don't have a trained model yet, set `DERMA_DEMO_MODE=True` in your `.env` file. The app will return synthetic predictions based on image hashing.

## Training the Model

The model can be trained on Google Colab using the included training script:

1. Upload `colab_trainer.py` to a Colab notebook.
2. Follow the instructions in `colab_training_guide.md`.
3. Download the resulting `derma_inceptionv3.keras` file.
4. Place it in the project root directory.

The model is trained on 7 skin condition classes using transfer learning on InceptionV3.

## API Endpoints

| Method | Route | Description |
|---|---|---|
| `GET` | `/` | Upload page |
| `POST` | `/predict` | Submit an image for diagnosis |
| `GET` | `/status/<task_id>` | Poll for async prediction result |
| `GET` | `/health` | Health check (model status, demo mode) |
| `GET` | `/docs` | API documentation |
| `GET` | `/privacy` | Privacy policy |
| `GET` | `/terms` | Terms of use |

## Run Tests

```powershell
pytest
```

## Project Structure

```
AI-Diagnostic/
├── app/
│   ├── __init__.py          # Package init
│   ├── diagnostic.py        # Model loading, preprocessing, inference
│   └── web.py               # Flask routes, async task queue
├── templates/               # Jinja2 HTML templates
├── static/                  # CSS, JS, images
├── tests/                   # Pytest test suite
├── colab_trainer.py         # Google Colab training script
├── colab_training_guide.md  # Training instructions
├── requirements.txt         # Python dependencies
├── run.py                   # Application entry point
└── .env                     # Environment configuration (not tracked)
```

## Privacy Boundary

This prototype does not create accounts, save images, store patient details, or keep result history. It is an educational decision-support demo and is not a replacement for clinical judgment.
