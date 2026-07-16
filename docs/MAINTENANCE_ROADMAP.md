# Maintenance Roadmap

This document outlines the ongoing maintenance strategy for the AI Dermatology Diagnostic Support application, covering both the software platform and the AI model.

---

## Table of Contents

1. [Maintenance Philosophy](#maintenance-philosophy)
2. [Routine Maintenance Schedule](#routine-maintenance-schedule)
3. [Model Maintenance](#model-maintenance)
4. [Software Updates](#software-updates)
5. [Database Maintenance](#database-maintenance)
6. [Security Maintenance](#security-maintenance)
7. [Feature Roadmap](#feature-roadmap)
8. [End-of-Life Planning](#end-of-life-planning)

---

## Maintenance Philosophy

This application combines a traditional web platform with an AI inference component. Both require distinct maintenance approaches:

- **Platform maintenance** follows standard software engineering practices — dependency updates, security patches, and infrastructure monitoring.
- **Model maintenance** follows MLOps practices — data drift detection, retraining schedules, and performance benchmarking.

---

## Routine Maintenance Schedule

### Weekly

| Task                                | Owner       | Notes                                |
| ----------------------------------- | ----------- | ------------------------------------ |
| Review application logs for errors  | SysAdmin    | Check for recurring inference errors |
| Verify `/health` endpoint status    | SysAdmin    | Automated via monitoring tool        |
| Review feedback submissions         | Clinical    | Look for patterns in clinical overrides |

### Monthly

| Task                                    | Owner       | Notes                                    |
| --------------------------------------- | ----------- | ---------------------------------------- |
| Update Python dependencies              | Developer   | `pip list --outdated`, test, then update |
| Review analytics database growth        | SysAdmin    | Archive old records if needed            |
| Check disk space on server              | SysAdmin    | Model + DB + logs                        |
| Export feedback data for model review   | Data Team   | CSV export from `diagnostic_logs`        |

### Quarterly

| Task                                    | Owner       | Notes                                    |
| --------------------------------------- | ----------- | ---------------------------------------- |
| Full security audit                     | SysAdmin    | Dependencies, configs, access controls   |
| Model performance review               | Data Team   | Compare predictions vs clinical overrides |
| Evaluate model retraining need          | Data Team   | Based on feedback and drift analysis     |
| Update documentation                   | Developer   | Reflect any changes in guides            |

### Annually

| Task                                    | Owner       | Notes                                    |
| --------------------------------------- | ----------- | ---------------------------------------- |
| Major version dependency upgrades       | Developer   | Python, Flask, TensorFlow                |
| Model architecture evaluation           | Data Team   | Consider newer architectures             |
| Infrastructure capacity review          | SysAdmin    | Scale up if usage has grown              |
| Regulatory compliance check             | Legal       | Data protection, medical device rules    |

---

## Model Maintenance

### Performance Monitoring

Use the `diagnostic_logs` table to track model performance over time:

```sql
-- Average confidence by condition (last 30 days)
SELECT predicted_condition,
       ROUND(AVG(confidence), 3) as avg_confidence,
       COUNT(*) as total
FROM diagnostic_logs
WHERE timestamp > datetime('now', '-30 days')
GROUP BY predicted_condition
ORDER BY total DESC;

-- Clinical override rate (indicator of model disagreement)
SELECT COUNT(CASE WHEN clinical_override IS NOT NULL THEN 1 END) as overridden,
       COUNT(*) as total,
       ROUND(100.0 * COUNT(CASE WHEN clinical_override IS NOT NULL THEN 1 END) / COUNT(*), 1) as override_pct
FROM diagnostic_logs
WHERE timestamp > datetime('now', '-30 days');

-- Average helpfulness rating
SELECT ROUND(AVG(helpful_rating), 2) as avg_rating,
       COUNT(*) as rated_count
FROM diagnostic_logs
WHERE helpful_rating IS NOT NULL
  AND timestamp > datetime('now', '-30 days');
```

### Retraining Triggers

Consider retraining the model when:

1. **Clinical override rate exceeds 20%** — Health workers frequently disagree with predictions.
2. **Average helpfulness rating drops below 3.0** — Users find the tool unhelpful.
3. **Confidence drift** — Average confidence scores shift significantly without explanation.
4. **New conditions added** — The scope of supported diagnoses expands.
5. **New training data becomes available** — Larger or more diverse datasets are sourced.

### Retraining Process

1. Export feedback data and clinical overrides from `diagnostic_logs`.
2. Source additional training images from verified dermatological datasets.
3. Retrain the InceptionV3 model using `colab_trainer.py` (see `colab_training_guide.md`).
4. Validate the new model against a held-out test set.
5. Compare accuracy against the previous model version.
6. Deploy the new `.keras` file to `DERMA_MODEL_PATH`.
7. Restart the application and verify via `/health`.

### Model Versioning

Adopt a naming convention for model files:

```
derma_inceptionv3_v1.0.keras   # Initial model
derma_inceptionv3_v1.1.keras   # Retrained with feedback data
derma_inceptionv3_v2.0.keras   # New architecture or major change
```

Keep at least 2 previous versions for rollback capability.

---

## Software Updates

### Dependency Update Procedure

```bash
# 1. Check for outdated packages
pip list --outdated

# 2. Update in a development environment first
pip install --upgrade Flask Pillow numpy python-json-logger

# 3. Run the test suite
pytest

# 4. Update requirements.txt with tested versions
pip freeze > requirements.txt

# 5. Commit, test on staging, then deploy
```

### Critical Updates

Apply immediately when security advisories are issued for:

- **Flask** — Web framework vulnerabilities
- **Pillow** — Image processing vulnerabilities (common attack vector)
- **TensorFlow** — Model loading vulnerabilities
- **SQLAlchemy** — Database injection risks

Subscribe to:
- [Flask Security Advisories](https://github.com/pallets/flask/security)
- [Pillow Security Advisories](https://github.com/python-pillow/Pillow/security)
- [TensorFlow Security Advisories](https://github.com/tensorflow/tensorflow/security)

---

## Database Maintenance

### Growth Estimation

Each diagnostic log record is approximately 200–500 bytes. At 100 diagnoses per day:

| Period  | Estimated Size |
| ------- | -------------- |
| 1 month | ~1.5 MB        |
| 1 year  | ~18 MB         |
| 5 years | ~90 MB         |

SQLite handles databases up to 281 TB, so storage is not a near-term concern.

### Archival Strategy

For long-running deployments, archive old records periodically:

```sql
-- Export records older than 1 year to CSV, then delete
.headers on
.mode csv
.output archive_2025.csv
SELECT * FROM diagnostic_logs WHERE timestamp < '2026-01-01';
.output stdout

DELETE FROM diagnostic_logs WHERE timestamp < '2026-01-01';
VACUUM;
```

### Scaling Beyond SQLite

If the application grows to serve multiple facilities with high throughput, consider migrating to PostgreSQL:

1. Update `DATABASE_URL` in `.env`:
   ```env
   DATABASE_URL=postgresql://user:password@localhost:5432/ai_diagnostic
   ```
2. Install the driver: `pip install psycopg2-binary`
3. Run `flask db upgrade` to apply the schema to PostgreSQL.

---

## Security Maintenance

### Monthly Security Tasks

- [ ] Run `pip audit` to check for known vulnerabilities.
- [ ] Review access logs for suspicious activity.
- [ ] Verify TLS certificate is valid and not expiring soon.
- [ ] Confirm `.env` file permissions are restricted.
- [ ] Check that debug mode is disabled in production.

### Incident Response

If a security incident is suspected:

1. **Isolate:** Take the application offline.
2. **Preserve:** Copy logs and database before making changes.
3. **Investigate:** Review access logs, application logs, and database queries.
4. **Remediate:** Patch the vulnerability, rotate any credentials.
5. **Restore:** Redeploy from a clean source and verified backup.
6. **Report:** Document the incident and notify stakeholders.

---

## Feature Roadmap

### Short-Term (Next 3 Months)

- [ ] Add dashboard for viewing aggregated analytics (condition frequency by region).
- [ ] Implement API authentication for multi-facility deployments.
- [ ] Add CSV/PDF export for diagnostic reports.

### Medium-Term (3–6 Months)

- [ ] Support additional skin conditions (expand beyond 7 classes).
- [ ] Add batch upload capability for retrospective analysis.
- [ ] Implement user accounts for health workers (optional, role-based).
- [ ] Add localization / multi-language support (Yoruba, Hausa, Igbo).

### Long-Term (6–12 Months)

- [ ] Migrate to a more modern model architecture (EfficientNet, Vision Transformer).
- [ ] Add offline capability via Progressive Web App (PWA) with on-device inference.
- [ ] Integration with hospital information systems (HL7 FHIR).
- [ ] Mobile app (React Native / Flutter) for improved camera access.

---

## End-of-Life Planning

When the application is no longer maintained:

1. **Notify users** at least 90 days before shutdown.
2. **Export all analytics data** and provide to stakeholders.
3. **Archive the codebase** on GitHub (mark as archived).
4. **Remove deployed instances** and revoke any credentials.
5. **Document lessons learned** for future projects.
