# Deployment Guide

This document describes how to deploy the AI Dermatology Diagnostic Support application from a local development environment through to a production-ready server.

---

## Table of Contents

1. [Prerequisites](#prerequisites)
2. [Environment Configuration](#environment-configuration)
3. [Local Development](#local-development)
4. [Database Setup](#database-setup)
5. [Production Deployment](#production-deployment)
6. [Docker Deployment (Optional)](#docker-deployment-optional)
7. [Reverse Proxy Configuration](#reverse-proxy-configuration)
8. [Health Checks](#health-checks)
9. [Security Checklist](#security-checklist)

---

## Prerequisites

| Requirement       | Version            | Notes                                    |
| ----------------- | ------------------ | ---------------------------------------- |
| Python            | 3.12.x             | TensorFlow does not yet support 3.13+    |
| pip               | latest stable      | Package installer                        |
| Git               | any recent version | Source control                           |
| Trained model     | —                  | `derma_inceptionv3.keras` (see Training) |

### Python Dependencies

All required packages are listed in `requirements.txt`:

```
Flask>=3.0.3
Pillow>=10.4.0
numpy>=1.26.0
pytest>=8.3.2
python-json-logger>=2.0.0
python-dotenv>=1.0.0
Flask-SQLAlchemy
Flask-Migrate

# Optional: install only when you have a real .keras model to load.
tensorflow>=2.15.0
```

> **Note:** TensorFlow is only needed when running with a real trained model. In demo mode it is not required.

---

## Environment Configuration

Create a `.env` file in the project root. This file is loaded automatically by `python-dotenv`.

```env
# Required
DERMA_DEMO_MODE=False
DERMA_MODEL_PATH=derma_inceptionv3.keras

# Optional
MAX_UPLOAD_MB=8
FLASK_DEBUG=0
DATABASE_URL=sqlite:///analytics.db
```

### Variable Reference

| Variable           | Default                      | Description                                      |
| ------------------ | ---------------------------- | ------------------------------------------------ |
| `DERMA_MODEL_PATH` | `derma_inceptionv3.keras`    | Path to the trained Keras model file              |
| `DERMA_DEMO_MODE`  | `False`                      | `True` to run without a real model (hash-based)   |
| `MAX_UPLOAD_MB`    | `8`                          | Maximum image upload size in megabytes            |
| `FLASK_DEBUG`      | `0`                          | `1` enables Flask debug mode (never in prod)      |
| `DATABASE_URL`     | `sqlite:///analytics.db`     | SQLAlchemy database URI for analytics logging     |

---

## Local Development

```powershell
# 1. Clone the repository
git clone https://github.com/Emmy042/AI-Diagnostic.git
cd AI-Diagnostic

# 2. Create and activate a virtual environment
py -3.12 -m venv .venv
.\.venv\Scripts\Activate.ps1

# 3. Install dependencies
pip install -r requirements.txt

# 4. Create .env file
@"
DERMA_DEMO_MODE=True
DERMA_MODEL_PATH=derma_inceptionv3.keras
"@ | Out-File -Encoding utf8 .env

# 5. Initialize the database
$env:FLASK_APP="run.py"
flask db init
flask db migrate -m "Initial schema"
flask db upgrade

# 6. Run the development server
python run.py
```

The app will be available at `http://127.0.0.1:5000`.

---

## Database Setup

The application uses SQLite (via SQLAlchemy + Flask-Migrate/Alembic) for non-identifiable diagnostic analytics.

### First-Time Initialization

```powershell
$env:FLASK_APP = "run.py"
flask db init          # Creates the migrations/ directory
flask db migrate -m "Initial schema"   # Generates migration script
flask db upgrade       # Applies the migration to create tables
```

### After Model Changes

If you modify `app/models.py`, generate and apply a new migration:

```powershell
flask db migrate -m "Description of change"
flask db upgrade
```

### Database Location

By default the analytics database is stored at `instance/analytics.db` (relative to the project root). You can override this with the `DATABASE_URL` environment variable.

---

## Production Deployment

> **Important:** Never use `python run.py` in production. Use a WSGI server.

### Option A: Gunicorn (Linux / macOS)

```bash
pip install gunicorn

# Run with 4 worker processes
gunicorn --bind 0.0.0.0:8000 --workers 4 --timeout 120 "run:app"
```

### Option B: Waitress (Windows)

```powershell
pip install waitress

# Run with 4 threads
python -c "from waitress import serve; from run import app; serve(app, host='0.0.0.0', port=8000, threads=4)"
```

### Production Environment Variables

```env
DERMA_DEMO_MODE=False
DERMA_MODEL_PATH=/opt/ai-diagnostic/models/derma_inceptionv3.keras
MAX_UPLOAD_MB=8
FLASK_DEBUG=0
DATABASE_URL=sqlite:////var/lib/ai-diagnostic/analytics.db
```

---

## Docker Deployment (Optional)

Create a `Dockerfile` in the project root:

```dockerfile
FROM python:3.12-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt gunicorn

COPY . .

# Initialize the database
RUN flask db upgrade || true

EXPOSE 8000

CMD ["gunicorn", "--bind", "0.0.0.0:8000", "--workers", "2", "--timeout", "120", "run:app"]
```

Build and run:

```bash
docker build -t ai-diagnostic .
docker run -d -p 8000:8000 \
  -e DERMA_DEMO_MODE=True \
  -v /path/to/models:/app/models \
  -v /path/to/data:/app/instance \
  ai-diagnostic
```

---

## Reverse Proxy Configuration

### Nginx Example

```nginx
server {
    listen 80;
    server_name diagnostic.example.com;

    client_max_body_size 10M;

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_read_timeout 120s;
    }
}
```

---

## Health Checks

The `/health` endpoint returns JSON with the application status:

```json
{
  "status": "ok",
  "demo_mode": false,
  "model_path": "derma_inceptionv3.keras",
  "model_loaded": true
}
```

Use this for load balancer health checks and monitoring systems.

---

## Security Checklist

- [ ] `FLASK_DEBUG` is set to `0` in production.
- [ ] `.env` file is NOT committed to version control.
- [ ] `tasks.db` and `analytics.db` are excluded from public access.
- [ ] A reverse proxy (Nginx/Apache) handles TLS termination.
- [ ] `client_max_body_size` is configured to match `MAX_UPLOAD_MB`.
- [ ] File uploads are validated server-side (extension + PIL verify).
- [ ] No patient images or PII are stored persistently.
- [ ] Database backups are scheduled for `analytics.db`.
