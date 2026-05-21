# Phase 3 Handoff: Implementation

## Implemented Files

- `app/diagnostic.py`: upload validation, preprocessing, result metadata, real/demo classifier.
- `app/web.py`: Flask app factory, `/`, `/predict`, and `/health`.
- `run.py`: local development entrypoint.
- `templates/`: upload, result, and error pages.
- `static/styles.css`: responsive healthcare UI styling.
- `requirements.txt`: runtime and test dependencies.
- `tests/`: core and Flask route tests written before implementation.

## Important Behaviors

- Missing model files automatically place the classifier in demo mode.
- `DERMA_DEMO_MODE=1` explicitly forces demo mode.
- Uploaded images are read from request streams and are not saved.
- Invalid uploads return HTTP 400 with a user-facing error page.
- Missing model/TensorFlow in non-demo mode returns HTTP 503.

## Phase Status

Phase 3 complete. Phase 4 should run tests when Python and pytest are available.
