# Project Progress

This file is the project's implementation log.

## Milestones Reached
- Project protocol established.
- Next.js MVP application initialization planned.
- Basic MVP application completed and deployed to `frontend/`.
- Accessible UI components implemented (`AccessibleButton`, `CameraView`, `ThemeToggle`).
- Native Dark Mode functionality via `next-themes` successfully integrated.
- Web Speech API integration verified for voice feedback.
- Application builds successfully without type errors.

## Database Analytics Layer (July 2026)
- Created `app/models.py` with `DiagnosticLog` SQLAlchemy model.
- Integrated Flask-SQLAlchemy and Flask-Migrate into the app factory (`app/web.py`).
- Added 1-5 star rating feedback UI and clinical override to `templates/result.html`.
- Created `/feedback/<log_id>` API endpoint for async feedback submission.

## Facility Management Update (July 2026)
- Migrated facility and region tracking from free-text strings to relational tables (`Region` and `Facility`).
- Added an API endpoint `/api/facilities` to serve dynamic region/facility choices.
- Improved the Frontend UX with a "Clinic Settings" modal that remembers the user's facility using `localStorage`. This eliminates the need to manually enter facility data on every upload.
- Created `seed_db.py` to auto-populate the database with example Nigerian regions and facilities.

## Documentation (July 2026)
- Created `docs/DEPLOYMENT.md` — full deployment guide (local, production, Docker, reverse proxy).
- Created `docs/USER_GUIDE.md` — step-by-step guide for health workers.
- Created `docs/SYSADMIN_GUIDE.md` — installation, monitoring, backup, troubleshooting.
- Created `docs/MAINTENANCE_ROADMAP.md` — routine schedules, model retraining, feature roadmap.
- Updated `context.md`, `progress.md`, and `todo.md` to reflect all changes.

## Codebase Refactoring & Bug Fixes (July 2026)
- Removed unused Next.js `frontend/` directory.
- Refactored `colab_trainer.py` and `train_model.py` to remove excessively verbose AI-generated comments and unused imports.
- Fixed `tests/test_flask_app.py` failing due to the web app's transition to background processing logic. All 11 tests now pass.
- Added confidence thresholding logic to `app/diagnostic.py` (<60% confidence returns "Unknown") to handle non-skin images gracefully.
- Fixed severe class imbalance in `colab_trainer.py` by computing and applying `class_weight` during model training.
