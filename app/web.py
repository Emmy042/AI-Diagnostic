from __future__ import annotations

import os
from pathlib import Path

from flask import Flask, jsonify, render_template, request

from app.diagnostic import DermaClassifier, ImageUpload, UnsupportedFileError


def create_app(config: dict | None = None) -> Flask:
    app = Flask(__name__, template_folder="../templates", static_folder="../static", instance_relative_config=False)
    app.config.update(
        DERMA_MODEL_PATH=os.getenv("DERMA_MODEL_PATH", "derma_inceptionv3.keras"),
        DERMA_DEMO_MODE=_parse_bool(os.getenv("DERMA_DEMO_MODE", "")),
        MAX_UPLOAD_MB=int(os.getenv("MAX_UPLOAD_MB", "8")),
        MAX_CONTENT_LENGTH=int(os.getenv("MAX_UPLOAD_MB", "8")) * 1024 * 1024,
    )
    if config:
        app.config.update(config)

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

        try:
            image = ImageUpload(
                filename=uploaded.filename,
                stream=uploaded.stream,
                max_bytes=int(app.config["MAX_UPLOAD_MB"]) * 1024 * 1024,
            ).open_image()
            result = classifier.predict(image)
        except UnsupportedFileError:
            return _error("Please upload a valid image in JPG, PNG, or WEBP format.", 400)
        except RuntimeError as exc:
            return _error(str(exc), 503)

        return render_template("result.html", result=result)

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
