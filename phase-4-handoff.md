# Phase 4 Handoff: Testing & Quality Assurance

## Tests Added

- `tests/test_diagnostic_core.py`
  - Valid image acceptance.
  - Invalid extension rejection.
  - Corrupted image rejection.
  - Oversized upload rejection.
  - InceptionV3-compatible preprocessing shape.
  - Demo classifier supported-label output.
  - Melanoma urgent referral guidance.
- `tests/test_flask_app.py`
  - Upload page load.
  - Valid prediction route.
  - Invalid upload route.
  - `/health` demo-mode status.

## Verification Attempt

Command attempted:

```powershell
pytest
```

Result:

`pytest` is not recognized in the current shell. The available `python.exe`, `python3.exe`, and `py.exe` commands point to Windows Store aliases and fail with a logon-session error, so tests could not be executed here.

## Phase Status

Phase 4 is complete with an environment limitation. After installing Python 3.11+ and dependencies, rerun `pytest`.
