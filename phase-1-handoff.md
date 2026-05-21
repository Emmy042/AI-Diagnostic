# Phase 1 Handoff: Requirements

## Product Goal

Build a school-project prototype of an AI-based diagnostic support system for dermatological conditions using deep learning concepts from Chapter 3.

## Target Users

- Primary healthcare workers
- General practitioners
- Community health extension workers
- School project evaluators reviewing the prototype

## Functional Requirements

- Allow a user to upload one skin image through a browser.
- Accept `.jpg`, `.jpeg`, `.png`, and `.webp` image files.
- Reject invalid file types, corrupted images, and oversized uploads.
- Preprocess accepted images into InceptionV3-compatible input.
- Return one likely condition from seven supported labels.
- Display confidence score, clinical note, referral recommendation, and medical disclaimer.
- Support browser print/download of the current result only.
- Provide a `/health` endpoint showing app readiness and whether demo mode is active.

## Non-Functional Requirements

- Run locally on a laptop with Flask.
- Avoid database, login, account management, patient history, and image persistence.
- Process uploaded images in memory/request scope only.
- Include automated tests for validation, preprocessing, classifier behavior, and Flask routes.
- Support demo mode when no trained Keras model exists.

## Out of Scope

- Full dataset collection and training pipeline.
- Clinical validation.
- Cloud deployment.
- Admin dashboard.
- Patient record management.

## Phase Status

Phase 1 complete. Phase 2 should use this handoff to define the architecture and module boundaries.
