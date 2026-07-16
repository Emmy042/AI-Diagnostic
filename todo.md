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

## Remaining Work
- Install missing Python dependencies (`numpy`, `Pillow`) — blocked by network issues.
- Run database migrations (`flask db init`, `flask db migrate`, `flask db upgrade`).
- Update `requirements.txt` to include `Flask-SQLAlchemy` and `Flask-Migrate`.
- Verify the full end-to-end workflow (upload → predict → feedback).
- Push latest documentation to GitHub.

## Future Improvements
- Add analytics dashboard for viewing condition frequency by region.
- Add API authentication for multi-facility deployments.
- Support additional skin conditions (expand beyond 7 classes).
- Add localization / multi-language support.
- Consider offline PWA capability with on-device inference.
