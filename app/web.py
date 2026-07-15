from __future__ import annotations

import os
import uuid
import json
import sqlite3
import logging
import time
from pythonjsonlogger import jsonlogger
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
import dataclasses

from flask import Flask, jsonify, render_template, request
from flask_migrate import Migrate

from app.diagnostic import DermaClassifier, ImageUpload, UnsupportedFileError
from app.models import db, DiagnosticLog

_executor = ThreadPoolExecutor(max_workers=2)
DB_PATH = "tasks.db"

def init_db():
    with sqlite3.connect(DB_PATH) as conn:
        conn.execute("CREATE TABLE IF NOT EXISTS tasks (id TEXT PRIMARY KEY, status TEXT, result TEXT, message TEXT)")

def update_task(task_id: str, status: str, result: dict | None = None, message: str | None = None):
    with sqlite3.connect(DB_PATH) as conn:
        conn.execute(
            "INSERT INTO tasks (id, status, result, message) VALUES (?, ?, ?, ?) "
            "ON CONFLICT(id) DO UPDATE SET status=excluded.status, result=excluded.result, message=excluded.message",
            (task_id, status, json.dumps(result) if result else None, message)
        )

def get_task(task_id: str) -> dict | None:
    with sqlite3.connect(DB_PATH) as conn:
        row = conn.execute("SELECT status, result, message FROM tasks WHERE id=?", (task_id,)).fetchone()
        if row:
            return {
                "status": row[0],
                "result": json.loads(row[1]) if row[1] else None,
                "message": row[2]
            }
        return None

def delete_task(task_id: str):
    with sqlite3.connect(DB_PATH) as conn:
        conn.execute("DELETE FROM tasks WHERE id=?", (task_id,))

def configure_logging(app: Flask):
    logHandler = logging.StreamHandler()
    formatter = jsonlogger.JsonFormatter('%(asctime)s %(levelname)s %(message)s')
    logHandler.setFormatter(formatter)
    app.logger.handlers.clear()
    app.logger.addHandler(logHandler)
    app.logger.setLevel(logging.INFO)

def create_app(config: dict | None = None) -> Flask:
    app = Flask(__name__, template_folder="../templates", static_folder="../static", instance_relative_config=False)
    configure_logging(app)
    init_db()

    app.config.update(
        DERMA_MODEL_PATH=os.getenv("DERMA_MODEL_PATH", "derma_inceptionv3.keras"),
        DERMA_DEMO_MODE=_parse_bool(os.getenv("DERMA_DEMO_MODE", "")),
        MAX_UPLOAD_MB=int(os.getenv("MAX_UPLOAD_MB", "8")),
        MAX_CONTENT_LENGTH=int(os.getenv("MAX_UPLOAD_MB", "8")) * 1024 * 1024,
        SQLALCHEMY_DATABASE_URI=os.getenv("DATABASE_URL", "sqlite:///analytics.db"),
        SQLALCHEMY_TRACK_MODIFICATIONS=False
    )
    if config:
        app.config.update(config)

    db.init_app(app)
    Migrate(app, db)

    model_path = Path(app.config["DERMA_MODEL_PATH"])
    classifier = DermaClassifier(
        model_path=model_path,
        demo_mode=bool(app.config["DERMA_DEMO_MODE"]),
    )
    app.extensions["derma_classifier"] = classifier

    @app.get("/")
    def index():
        return render_template("index.html", demo_mode=classifier.demo_mode)

    @app.post("/predict")
    def predict():
        uploaded = request.files.get("image")
        if uploaded is None or uploaded.filename == "":
            return _error("Please upload a valid image before requesting a diagnosis.", 400)
            
        facility_name = request.form.get("facility_name")
        region = request.form.get("region")
        user_agent = request.headers.get("User-Agent")

        try:
            image = ImageUpload(
                filename=uploaded.filename,
                stream=uploaded.stream,
                max_bytes=int(app.config["MAX_UPLOAD_MB"]) * 1024 * 1024,
            ).open_image()
        except UnsupportedFileError:
            app.logger.warning("Upload rejected: unsupported file format.")
            return _error("Please upload a valid image in JPG, PNG, or WEBP format.", 400)
        except Exception as exc:
            app.logger.error("Failed to read image upload: %s", exc)
            return _error("An internal error occurred during diagnosis. Please try again later.", 503)

        task_id = str(uuid.uuid4())
        update_task(task_id, "processing")

        def run_prediction(t_id, img, fac_name, reg, ua):
            start_time = time.time()
            try:
                res = classifier.predict(img)
                duration_ms = int((time.time() - start_time) * 1000)
                
                with app.app_context():
                    log_entry = DiagnosticLog(
                        predicted_condition=res.condition,
                        confidence=res.confidence,
                        task_duration_ms=duration_ms,
                        outcome="success",
                        facility_name=fac_name,
                        region=reg,
                        device_type=ua
                    )
                    db.session.add(log_entry)
                    db.session.commit()
                    log_id = log_entry.id
                
                res_dict = dataclasses.asdict(res)
                res_dict["log_id"] = log_id
                
                update_task(t_id, "done", result=res_dict)
            except Exception as exc:
                app.logger.error("Inference failed for task %s: %s", t_id, exc)
                update_task(t_id, "error", message="An internal error occurred during diagnosis. Please try again later.")

        _executor.submit(run_prediction, task_id, image, facility_name, region, user_agent)
        app.logger.info("Started inference task %s", task_id)
        return render_template("processing.html", task_id=task_id)

    @app.get("/status/<task_id>")
    def status(task_id):
        task = get_task(task_id)
        if not task:
            return _error("Task not found or expired.", 404)
            
        if task["status"] == "processing":
            return render_template("processing.html", task_id=task_id)
        elif task["status"] == "done":
            result = task["result"]
            delete_task(task_id)
            app.logger.info("Task %s completed successfully", task_id)
            return render_template("result.html", result=result)
        else:
            msg = task["message"] or "Unknown error"
            delete_task(task_id)
            return _error(msg, 503)

    @app.post("/feedback/<int:log_id>")
    def feedback(log_id):
        rating = request.form.get("rating")
        override = request.form.get("override")
        
        log_entry = db.session.get(DiagnosticLog, log_id)
        if log_entry:
            if rating:
                try:
                    log_entry.helpful_rating = int(rating)
                except ValueError:
                    pass
            if override:
                log_entry.clinical_override = override
            db.session.commit()
            return jsonify({"status": "success"})
        return jsonify({"status": "error", "message": "Log not found"}), 404

    @app.get("/docs")
    def docs():
        return render_template("docs.html")

    @app.get("/privacy")
    def privacy():
        return render_template("privacy.html")

    @app.get("/terms")
    def terms():
        return render_template("terms.html")

    @app.get("/health")
    def health():
        return jsonify(
            {
                "status": "ok" if classifier.ready else "model_unavailable",
                "demo_mode": classifier.demo_mode,
                "model_path": str(model_path),
                "model_loaded": classifier._model is not None,
            }
        )

    def _error(message: str, status_code: int):
        return render_template("error.html", message=message), status_code

    return app

def _parse_bool(value: str | bool) -> bool:
    if isinstance(value, bool):
        return value
    return str(value).strip().lower() in {"1", "true", "yes", "on"}
