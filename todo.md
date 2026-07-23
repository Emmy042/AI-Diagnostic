# Project Todo

This file is the project's task tracker.

## Completed
- [x] Create deployment documentation and packaging for production.
- [x] Write a user guide for health workers on how to use the diagnostic tool.
- [x] Write a system administrator guide.
- [x] Create a maintenance roadmap for the application and model.
- [x] Add database analytics layer (DiagnosticLog model, Flask-SQLAlchemy/Migrate).
- [x] Add user feedback system (1-5 star rating, clinical override).
- [x] Add optional facility/region metadata fields.
- [x] Install missing Python dependencies (`numpy`, `Pillow`).
- [x] Run database migrations (`flask db init`, `flask db migrate`, `flask db upgrade`).
- [x] Verify the full end-to-end workflow (upload → predict → feedback).
- [x] Clean up unused directories (removed `frontend/`).
- [x] Remove AI-generated tutorial comments from training scripts.
- [x] Fix broken unit tests and ensure the test suite is 100% passing.
- [x] Implement out-of-distribution detection (confidence threshold) for the classifier.
- [x] Fix dataset class imbalance bias in `colab_trainer.py`.

## Highest-priority next task
- Run the updated `colab_trainer.py` script to train a new model and replace `derma_inceptionv3.keras` (to resolve the current model's heavy bias toward "Monkeypox").

## Future Improvements
- Add analytics dashboard for viewing condition frequency by region.
- Add API authentication for multi-facility deployments.
- Support additional skin conditions (expand beyond 7 classes).
- Add localization / multi-language support.
- Consider offline PWA capability with on-device inference.
