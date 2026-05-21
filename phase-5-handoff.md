# Phase 5 Handoff: Deployment & Release

## Local Demo Path

The app is intended to run locally with Flask:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
$env:DERMA_DEMO_MODE = "1"
python run.py
```

Open:

```text
http://127.0.0.1:5000
```

## Release Notes

- Demo mode is suitable for presentation when no trained model file exists.
- A real Keras model can be placed at `models/derma_inceptionv3.keras`.
- TensorFlow is intentionally optional because it is large and only needed for real model inference.

## Verification Attempt

Command attempted:

```powershell
flask --version
```

Result:

`flask` is not installed in the current shell, and Python is not currently runnable from this environment.

## Phase Status

Phase 5 is complete with an environment limitation. Runtime verification should be performed after installing Python and dependencies.
