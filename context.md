# Project Context

This file stores long-term project context.

## Overall Architecture
- **Backend**: Python Flask web application serving a web UI and handling image processing server-side.
- **AI Processing**: InceptionV3 deep learning model (`derma_inceptionv3.keras`) integrated for dermatological condition classification.

## Important Implementation Decisions
- Designed to solve the inability of non-specialist health workers to accurately identify skin diseases at the point of care in Nigerian healthcare facilities.
- Classifies 7 dermatological conditions: Melanoma, Eczema, Psoriasis, Acne Vulgaris, Tinea (Ringworm), Vitiligo, and Monkeypox.
- Provides a clinical note, confidence score, and referral recommendation for diagnosed images.
- Privacy-preserving design: Images and personal data are processed entirely in-memory and are not stored permanently.
- Accessible via any web browser on low-cost smartphones and tablets.

## Folder Structure
- `/app` - Core backend logic, routing (`web.py`), and AI classification inference (`diagnostic.py`).
- `/templates` - HTML templates for the web interface (index, processing, result, error, etc.).
- `/static` - Static assets for the web application.
- `train_model.py` - Script for training the InceptionV3 model.
- `run.py` - Application entry point.

## Known Constraints
- Requires the trained Keras model file (`derma_inceptionv3.keras`) to run in production mode; alternatively supports a mock demo mode for testing.
