# Phase 2 Handoff: Architecture

## Application Shape

The system is a single-process Flask application for a local school-project demo. It has no database, no background worker, no accounts, and no persistent upload storage.

## Module Boundaries

- `app.diagnostic`
  - Owns supported labels, clinical notes, upload validation, preprocessing, model/demo prediction, and result creation.
- `app.web`
  - Owns Flask app creation, routes, configuration, and template rendering.
- `templates`
  - Owns upload, result, and error pages.
- `static`
  - Owns CSS and small browser-side enhancements only.

## Runtime Contracts

- `GET /` renders the upload page.
- `POST /predict` accepts one multipart field named `image`.
- `GET /health` returns JSON readiness status.
- `DERMA_MODEL_PATH` defaults to `models/derma_inceptionv3.keras`.
- `DERMA_DEMO_MODE=1` forces demo mode.
- `MAX_UPLOAD_MB` defaults to `8`.

## Privacy Design

Uploaded images are opened from the request stream, processed in memory, and not written to project storage. Results are rendered for the current request only.

## Phase Status

Phase 2 complete. Phase 3 should read this handoff before implementing.
