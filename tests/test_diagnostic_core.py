import io

import numpy as np
import pytest
from PIL import Image

from app.diagnostic import (
    CLASS_LABELS,
    DiagnosticResult,
    ImageUpload,
    Preprocessor,
    UnsupportedFileError,
    DermaClassifier,
)


def make_image_bytes(fmt="PNG", size=(64, 64), color=(120, 80, 60)):
    stream = io.BytesIO()
    Image.new("RGB", size, color).save(stream, format=fmt)
    stream.seek(0)
    return stream


def test_valid_image_upload_is_accepted():
    upload = ImageUpload(filename="lesion.png", stream=make_image_bytes())

    image = upload.open_image()

    assert image.mode == "RGB"
    assert image.size == (64, 64)


def test_invalid_file_extension_is_rejected():
    upload = ImageUpload(filename="notes.txt", stream=io.BytesIO(b"not an image"))

    with pytest.raises(UnsupportedFileError):
        upload.open_image()


def test_corrupted_image_is_rejected():
    upload = ImageUpload(filename="lesion.jpg", stream=io.BytesIO(b"broken"))

    with pytest.raises(UnsupportedFileError):
        upload.open_image()


def test_oversized_upload_is_rejected():
    upload = ImageUpload(
        filename="lesion.png",
        stream=io.BytesIO(b"0" * 21),
        max_bytes=20,
    )

    with pytest.raises(UnsupportedFileError):
        upload.open_image()


def test_preprocessor_returns_inception_input_shape():
    preprocessor = Preprocessor()

    processed = preprocessor.transform(Image.new("RGB", (80, 80), (10, 20, 30)))

    assert processed.shape == (1, 299, 299, 3)
    assert processed.dtype == np.float32


def test_demo_classifier_returns_supported_label():
    classifier = DermaClassifier(model_path="missing.keras", demo_mode=True)

    result = classifier.predict(Image.new("RGB", (64, 64), (200, 120, 80)))

    assert result.condition in CLASS_LABELS
    assert 0 <= result.confidence <= 1
    assert result.is_demo_mode is True


def test_melanoma_result_requires_urgent_referral():
    result = DiagnosticResult.from_condition("Melanoma", 0.91, is_demo_mode=False)

    assert "urgent" in result.referral_recommendation.lower()
    assert result.condition == "Melanoma"
