# Project Context

This file stores long-term project context.

## Overall Architecture
- **Backend**: Python Flask web application serving a web UI and handling image processing server-side.
- **AI Processing**: InceptionV3 deep learning model (`derma_inceptionv3.keras`) integrated for dermatological condition classification.
- **Database**: SQLite via Flask-SQLAlchemy + Flask-Migrate for anonymized diagnostic analytics and user feedback.
- **Task Queue**: SQLite-based lightweight task queue for async inference with `ThreadPoolExecutor`.

## Important Implementation Decisions
- Designed to solve the inability of non-specialist health workers to accurately identify skin diseases at the point of care in Nigerian healthcare facilities.
- Classifies 7 dermatological conditions: Melanoma, Eczema, Psoriasis, Acne Vulgaris, Tinea (Ringworm), Vitiligo, and Monkeypox.
- Provides a clinical note, confidence score, and referral recommendation for diagnosed images.
- Privacy-preserving design: Images and personal data are processed entirely in-memory and are not stored permanently.
- Accessible via any web browser on low-cost smartphones and tablets.
- Database stores only non-identifiable analytics (condition, confidence, facility, region, feedback) — no images or PII.
- User feedback uses a 1-5 star helpfulness rating and optional clinical override text.
- Facility name and region are optional metadata fields.

## Folder Structure
- `/app` - Core backend logic, routing (`web.py`), AI classification inference (`diagnostic.py`), and database models (`models.py`).
- `/templates` - HTML templates for the web interface (index, processing, result, error, etc.).
- `/static` - Static assets for the web application.
- `/docs` - Project documentation (Deployment, User Guide, SysAdmin Guide, Maintenance Roadmap).
- `train_model.py` - Script for training the InceptionV3 model.
- `run.py` - Application entry point.

## API Endpoints
- `GET /` — Upload page
- `POST /predict` — Submit image for diagnosis (accepts optional `facility_name`, `region`)
- `GET /status/<task_id>` — Poll for async prediction result
- `POST /feedback/<log_id>` — Submit star rating and clinical override
- `GET /health` — Health check endpoint
- `GET /docs`, `/privacy`, `/terms` — Static info pages

## Known Constraints
- Requires the trained Keras model file (`derma_inceptionv3.keras`) to run in production mode; alternatively supports a mock demo mode for testing.
- TensorFlow is only required when running with a real model (not in demo mode).
- SQLite is suitable for single-facility deployment; PostgreSQL recommended for multi-facility scale.
