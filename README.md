# AI Dermatology Diagnostic Support

Local Flask prototype for a school project based on Chapter 3 of the AI dermatology diagnostic system document.

## What It Does

- Uploads one skin image through a browser.
- Validates JPG, PNG, and WEBP files.
- Runs InceptionV3-compatible preprocessing.
- Returns a predicted condition, confidence score, clinical note, and referral recommendation.
- Keeps uploads/results out of persistent storage.
- Supports demo mode when no trained Keras model is available.

## Supported Classes

- Melanoma
- Eczema
- Psoriasis
- Acne Vulgaris
- Tinea/Ringworm
- Vitiligo
- Monkeypox

## Setup

Install Python 3.11 or newer, then run:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
```

## Run Locally

Demo mode is recommended until a trained model is available:

```powershell
$env:DERMA_DEMO_MODE = "1"
python run.py
```

Open:

```text
http://127.0.0.1:5000
```

## Use a Real Model

Place the trained model at:

```text
models/derma_inceptionv3.keras
```

Then install TensorFlow, unset demo mode, and run:

```powershell
$env:DERMA_DEMO_MODE = "0"
python run.py
```

## Run Tests

```powershell
pytest
```

## Privacy Boundary

This prototype does not create accounts, save images, store patient details, or keep result history. It is an educational decision-support demo and is not a replacement for clinical judgment.
