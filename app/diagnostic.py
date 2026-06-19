from __future__ import annotations

import hashlib
from dataclasses import dataclass
from pathlib import Path
from typing import BinaryIO

import numpy as np
from PIL import Image, UnidentifiedImageError


CLASS_LABELS = (
    "Melanoma",
    "Eczema",
    "Psoriasis",
    "Acne Vulgaris",
    "Tinea/Ringworm",
    "Vitiligo",
    "Monkeypox",
)

ALLOWED_EXTENSIONS = {".jpg", ".jpeg", ".png", ".webp"}

CONDITION_NOTES = {
    "Melanoma": {
        "note": "A potentially serious skin cancer that needs prompt clinical assessment.",
        "referral": "Urgent referral to a dermatologist or oncology-capable facility is recommended.",
    },
    "Eczema": {
        "note": "An inflammatory skin condition often associated with itching, dryness, and recurrent flares.",
        "referral": "Review symptoms clinically and refer if severe, infected, widespread, or treatment-resistant.",
    },
    "Psoriasis": {
        "note": "A chronic inflammatory condition that may produce scaly plaques and recurring lesions.",
        "referral": "Refer if extensive, painful, joint symptoms are present, or diagnosis is uncertain.",
    },
    "Acne Vulgaris": {
        "note": "A common condition involving blocked follicles, inflammation, papules, pustules, or nodules.",
        "referral": "Refer if severe, scarring, psychologically distressing, or unresponsive to initial treatment.",
    },
    "Tinea/Ringworm": {
        "note": "A fungal skin infection that may appear as itchy, ring-shaped, or scaly patches.",
        "referral": "Consider laboratory confirmation or referral if recurrent, extensive, or involving scalp/nails.",
    },
    "Vitiligo": {
        "note": "A pigmentary disorder causing lighter depigmented patches on the skin.",
        "referral": "Refer for confirmation, counseling, and management options where available.",
    },
    "Monkeypox": {
        "note": "A viral illness that may include fever and characteristic skin lesions.",
        "referral": "Follow local public health guidance and refer/isolate when clinically suspected.",
    },
}


class UnsupportedFileError(ValueError):
    """Raised when an uploaded file cannot be safely used as an image."""


@dataclass(frozen=True)
class ImageUpload:
    filename: str
    stream: BinaryIO
    max_bytes: int = 8 * 1024 * 1024

    def open_image(self) -> Image.Image:
        suffix = Path(self.filename or "").suffix.lower()
        if suffix not in ALLOWED_EXTENSIONS:
            raise UnsupportedFileError("Please upload a valid image file.")

        data = self.stream.read()
        if not data:
            raise UnsupportedFileError("Please upload a non-empty image file.")
        if len(data) > self.max_bytes:
            raise UnsupportedFileError("The uploaded image is too large.")

        try:
            image = Image.open(_bytes_to_stream(data))
            image.verify()
            image = Image.open(_bytes_to_stream(data)).convert("RGB")
        except (UnidentifiedImageError, OSError, ValueError) as exc:
            raise UnsupportedFileError("Please upload a valid image file.") from exc

        return image


class Preprocessor:
    def __init__(self, target_size: tuple[int, int] = (299, 299)) -> None:
        self.target_size = target_size

    def transform(self, image: Image.Image) -> np.ndarray:
        resized = image.convert("RGB").resize(self.target_size)
        array = np.asarray(resized, dtype=np.float32)
        array = (array / 127.5) - 1.0
        return np.expand_dims(array, axis=0).astype(np.float32)


@dataclass(frozen=True)
class DiagnosticResult:
    condition: str
    confidence: float
    clinical_note: str
    referral_recommendation: str
    is_demo_mode: bool

    @classmethod
    def from_condition(
        cls,
        condition: str,
        confidence: float,
        is_demo_mode: bool,
    ) -> "DiagnosticResult":
        if condition not in CONDITION_NOTES:
            raise ValueError(f"Unsupported condition: {condition}")

        metadata = CONDITION_NOTES[condition]
        return cls(
            condition=condition,
            confidence=max(0.0, min(float(confidence), 1.0)),
            clinical_note=metadata["note"],
            referral_recommendation=metadata["referral"],
            is_demo_mode=is_demo_mode,
        )


class DermaClassifier:
    def __init__(
        self,
        model_path: str | Path,
        demo_mode: bool = False,
        preprocessor: Preprocessor | None = None,
    ) -> None:
        self.model_path = Path(model_path)
        self.demo_mode = demo_mode
        self.preprocessor = preprocessor or Preprocessor()
        self._model = None

        if not self.demo_mode:
            if not self.model_path.exists():
                raise FileNotFoundError(f"Model file not found at {self.model_path}. Cannot start in production mode.")
            self._model = self._load_model()

    @property
    def ready(self) -> bool:
        return self.demo_mode or self._model is not None

    def predict(self, image: Image.Image) -> DiagnosticResult:
        if self.demo_mode:
            return self._predict_demo(image)

        if self._model is None:
            raise RuntimeError("No trained model is loaded. Enable demo mode or provide a model file.")

        processed = self.preprocessor.transform(image)
        predictions = self._model.predict(processed, verbose=0)[0]
        best_index = int(np.argmax(predictions))
        return DiagnosticResult.from_condition(
            CLASS_LABELS[best_index],
            float(predictions[best_index]),
            is_demo_mode=False,
        )

    def _load_model(self):
        try:
            from tensorflow.keras.models import load_model
        except ImportError as exc:
            raise RuntimeError("TensorFlow is required to load a real Keras model.") from exc

        return load_model(self.model_path)

    def _predict_demo(self, image: Image.Image) -> DiagnosticResult:
        digest = hashlib.sha256(image.tobytes()).digest()
        index = digest[0] % len(CLASS_LABELS)
        confidence = 0.62 + ((digest[1] % 31) / 100)
        return DiagnosticResult.from_condition(
            CLASS_LABELS[index],
            confidence,
            is_demo_mode=True,
        )


def _bytes_to_stream(data: bytes):
    from io import BytesIO

    return BytesIO(data)
