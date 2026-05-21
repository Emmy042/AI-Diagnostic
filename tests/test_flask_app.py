import io

from PIL import Image

from app.web import create_app


def make_upload(fmt="PNG"):
    stream = io.BytesIO()
    Image.new("RGB", (64, 64), (100, 90, 80)).save(stream, format=fmt)
    stream.seek(0)
    return stream


def test_upload_page_loads():
    app = create_app({"TESTING": True, "DERMA_DEMO_MODE": True})

    response = app.test_client().get("/")

    assert response.status_code == 200
    assert b"AI Dermatology Diagnostic Support" in response.data


def test_predict_route_handles_valid_image():
    app = create_app({"TESTING": True, "DERMA_DEMO_MODE": True})

    response = app.test_client().post(
        "/predict",
        data={"image": (make_upload(), "lesion.png")},
        content_type="multipart/form-data",
    )

    assert response.status_code == 200
    assert b"Diagnostic Result" in response.data
    assert b"Demo mode" in response.data


def test_predict_route_rejects_invalid_image():
    app = create_app({"TESTING": True, "DERMA_DEMO_MODE": True})

    response = app.test_client().post(
        "/predict",
        data={"image": (io.BytesIO(b"hello"), "notes.txt")},
        content_type="multipart/form-data",
    )

    assert response.status_code == 400
    assert b"Please upload a valid image" in response.data


def test_health_reports_demo_mode():
    app = create_app({"TESTING": True, "DERMA_DEMO_MODE": True})

    response = app.test_client().get("/health")

    assert response.status_code == 200
    assert response.get_json()["demo_mode"] is True
