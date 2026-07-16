# System Administrator Guide

This guide covers installation, configuration, monitoring, backup, and troubleshooting of the AI Dermatology Diagnostic Support application for system administrators.

---

## Table of Contents

1. [System Requirements](#system-requirements)
2. [Installation](#installation)
3. [Configuration Reference](#configuration-reference)
4. [Database Administration](#database-administration)
5. [Logging and Monitoring](#logging-and-monitoring)
6. [Backup and Recovery](#backup-and-recovery)
7. [Performance Tuning](#performance-tuning)
8. [Security Hardening](#security-hardening)
9. [Troubleshooting](#troubleshooting)
10. [Common Operations](#common-operations)

---

## System Requirements

### Minimum (Demo Mode)

| Resource | Specification            |
| -------- | ------------------------ |
| CPU      | 2 cores                  |
| RAM      | 2 GB                     |
| Disk     | 500 MB                   |
| OS       | Windows 10+, Ubuntu 22+  |
| Python   | 3.12.x                   |

### Recommended (Production with TensorFlow)

| Resource | Specification            |
| -------- | ------------------------ |
| CPU      | 4+ cores                 |
| RAM      | 8 GB                     |
| Disk     | 5 GB                     |
| GPU      | Optional (CUDA-capable)  |
| OS       | Ubuntu 22.04 LTS         |
| Python   | 3.12.x                   |

---

## Installation

### Step 1: Clone and Set Up

```bash
git clone https://github.com/Emmy042/AI-Diagnostic.git
cd AI-Diagnostic

python3.12 -m venv .venv
source .venv/bin/activate     # Linux/macOS
# .\.venv\Scripts\Activate.ps1  # Windows

pip install -r requirements.txt
```

### Step 2: Configure Environment

```bash
cp .env.example .env   # Or create manually
nano .env
```

Minimum `.env` for production:

```env
DERMA_DEMO_MODE=False
DERMA_MODEL_PATH=/opt/ai-diagnostic/models/derma_inceptionv3.keras
MAX_UPLOAD_MB=8
FLASK_DEBUG=0
DATABASE_URL=sqlite:////var/lib/ai-diagnostic/analytics.db
```

### Step 3: Initialize Database

```bash
export FLASK_APP=run.py
flask db init
flask db migrate -m "Initial schema"
flask db upgrade
```

### Step 4: Deploy the Model File

Place the trained `derma_inceptionv3.keras` file at the path specified by `DERMA_MODEL_PATH`. Ensure the application process has read access to this file.

### Step 5: Start the Application

```bash
# Production (Linux)
gunicorn --bind 0.0.0.0:8000 --workers 4 --timeout 120 "run:app"

# Production (Windows)
waitress-serve --host=0.0.0.0 --port=8000 --threads=4 run:app
```

---

## Configuration Reference

| Variable           | Default                   | Description                                        |
| ------------------ | ------------------------- | -------------------------------------------------- |
| `DERMA_MODEL_PATH` | `derma_inceptionv3.keras` | Absolute path to the trained Keras model            |
| `DERMA_DEMO_MODE`  | `False`                   | `True` disables real model, uses hash-based output  |
| `MAX_UPLOAD_MB`    | `8`                       | Maximum image upload size in megabytes              |
| `FLASK_DEBUG`      | `0`                       | **Must be `0` in production**                       |
| `DATABASE_URL`     | `sqlite:///analytics.db`  | SQLAlchemy connection URI for analytics database    |

---

## Database Administration

### Schema Overview

The `diagnostic_logs` table stores anonymized diagnostic analytics:

| Column               | Type         | Description                          |
| -------------------- | ------------ | ------------------------------------ |
| `id`                 | Integer (PK) | Auto-incrementing primary key        |
| `timestamp`          | DateTime     | UTC timestamp of the diagnosis       |
| `predicted_condition`| String(100)  | AI-predicted skin condition          |
| `confidence`         | Float        | Confidence score (0.0–1.0)           |
| `task_duration_ms`   | Integer      | Inference duration in milliseconds   |
| `outcome`            | String(50)   | `success` or `error`                 |
| `facility_name`      | String(255)  | Optional facility identifier         |
| `region`             | String(100)  | Optional region/state                |
| `device_type`        | String(255)  | User-Agent string (device info)      |
| `helpful_rating`     | Integer      | 1–5 star feedback from health worker |
| `clinical_override`  | Text         | Clinician's corrected diagnosis      |

### Applying Migrations

After any change to `app/models.py`:

```bash
flask db migrate -m "Description of change"
flask db upgrade
```

### Viewing Data (SQLite)

```bash
sqlite3 instance/analytics.db
sqlite> .headers on
sqlite> .mode column
sqlite> SELECT predicted_condition, confidence, facility_name, helpful_rating FROM diagnostic_logs ORDER BY timestamp DESC LIMIT 20;
sqlite> .quit
```

### Exporting Data

```bash
sqlite3 -header -csv instance/analytics.db "SELECT * FROM diagnostic_logs;" > export.csv
```

---

## Logging and Monitoring

### Application Logs

The application uses structured JSON logging via `python-json-logger`. Log output goes to `stderr` by default.

Example log entry:

```json
{
  "asctime": "2026-07-16 10:30:15,123",
  "levelname": "INFO",
  "message": "Started inference task a1b2c3d4-..."
}
```

### Redirecting Logs to File

```bash
gunicorn --bind 0.0.0.0:8000 "run:app" \
  --access-logfile /var/log/ai-diagnostic/access.log \
  --error-logfile /var/log/ai-diagnostic/error.log
```

### Health Check Endpoint

```bash
curl http://localhost:8000/health
```

Response:

```json
{
  "status": "ok",
  "demo_mode": false,
  "model_path": "derma_inceptionv3.keras",
  "model_loaded": true
}
```

| `status` Value      | Meaning                            |
| -------------------- | ---------------------------------- |
| `ok`                 | Model loaded and ready             |
| `model_unavailable`  | Model file missing or failed to load |

### Recommended Monitoring

- Poll `/health` every 30 seconds from your monitoring tool (Uptime Kuma, Nagios, etc.).
- Alert on `status != "ok"` or HTTP response code != 200.
- Monitor disk usage for `analytics.db` growth.

---

## Backup and Recovery

### Database Backup

```bash
# Daily backup (add to cron)
cp /var/lib/ai-diagnostic/analytics.db /backups/analytics_$(date +%Y%m%d).db
```

Cron entry (daily at 2 AM):

```cron
0 2 * * * cp /var/lib/ai-diagnostic/analytics.db /backups/analytics_$(date +\%Y\%m\%d).db
```

### Model File Backup

The model file (`derma_inceptionv3.keras`) is large and should be stored in a separate backup location:

```bash
cp /opt/ai-diagnostic/models/derma_inceptionv3.keras /backups/models/
```

### Recovery Procedure

1. Stop the application service.
2. Restore the database file from backup.
3. Verify model file exists at `DERMA_MODEL_PATH`.
4. Restart the application.
5. Verify via `/health` endpoint.

---

## Performance Tuning

### Gunicorn Workers

Rule of thumb: `(2 × CPU cores) + 1`

```bash
# 4-core machine
gunicorn --workers 9 --timeout 120 "run:app"
```

### Timeout Configuration

TensorFlow inference can take 5–15 seconds. Set timeouts accordingly:

- Gunicorn: `--timeout 120`
- Nginx: `proxy_read_timeout 120s`
- Client polling interval: 2 seconds (configured in `processing.html`)

### Upload Size

Match `MAX_UPLOAD_MB` in `.env` with your reverse proxy configuration:

```nginx
client_max_body_size 10M;  # Slightly above MAX_UPLOAD_MB
```

---

## Security Hardening

### Production Checklist

- [ ] `FLASK_DEBUG=0` — Never enable debug mode in production.
- [ ] `.env` is readable only by the application user (`chmod 600 .env`).
- [ ] Database files are not accessible via the web server.
- [ ] TLS/HTTPS is enabled via reverse proxy (Nginx, Caddy, etc.).
- [ ] Upload validation is enforced server-side (extension + PIL verify).
- [ ] No patient PII or images are stored persistently.
- [ ] Application runs as a non-root user.
- [ ] File permissions are restricted (`chmod 750` on app directories).

### Firewall

Only expose the reverse proxy port (80/443). Keep the application port (8000) internal:

```bash
ufw allow 80/tcp
ufw allow 443/tcp
ufw deny 8000/tcp
```

---

## Troubleshooting

### Application Won't Start

| Symptom                          | Cause                                  | Fix                                          |
| -------------------------------- | -------------------------------------- | -------------------------------------------- |
| `ModuleNotFoundError: numpy`     | Missing dependency                     | `pip install -r requirements.txt`            |
| `FileNotFoundError: model`       | Model file not at `DERMA_MODEL_PATH`   | Verify path or set `DERMA_DEMO_MODE=True`    |
| `RuntimeError: TensorFlow`       | TensorFlow not installed               | `pip install tensorflow` or use demo mode    |
| Port already in use              | Another process on port 5000/8000      | `lsof -i :8000` and kill or change port      |

### Database Errors

| Symptom                          | Fix                                                       |
| -------------------------------- | --------------------------------------------------------- |
| `OperationalError: no such table`| Run `flask db upgrade`                                    |
| Database locked                  | Reduce concurrent writes or switch to PostgreSQL          |
| Migration conflict               | `flask db heads` → `flask db merge heads` → `flask db upgrade` |

### High Memory Usage

TensorFlow loads the full model into memory. On memory-constrained systems:

- Use only 1–2 Gunicorn workers.
- Consider enabling TensorFlow's memory growth settings.
- Monitor with `htop` or `top`.

---

## Common Operations

### Restart the Application (systemd)

```bash
sudo systemctl restart ai-diagnostic
```

### View Recent Logs

```bash
journalctl -u ai-diagnostic --since "1 hour ago" -f
```

### Check Database Size

```bash
du -h /var/lib/ai-diagnostic/analytics.db
```

### Count Total Diagnoses

```bash
sqlite3 /var/lib/ai-diagnostic/analytics.db "SELECT COUNT(*) FROM diagnostic_logs;"
```

### View Feedback Summary

```bash
sqlite3 -header -column /var/lib/ai-diagnostic/analytics.db \
  "SELECT predicted_condition, AVG(helpful_rating) as avg_rating, COUNT(*) as total FROM diagnostic_logs WHERE helpful_rating IS NOT NULL GROUP BY predicted_condition;"
```
