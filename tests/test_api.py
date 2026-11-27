from pathlib import Path

import pytest
from fastapi.testclient import TestClient

import app.main as service

SAMPLES = Path(__file__).resolve().parents[1] / "data" / "current"


@pytest.fixture
def client():
    with TestClient(service.app) as test_client:
        yield test_client


def test_health_and_readiness(client):
    health = client.get("/health")
    assert health.status_code == 200
    assert health.json() == {"status": "ok"}

    readiness = client.get("/ready")
    assert readiness.status_code == 200
    assert readiness.json() == {"status": "ready", "model_version": "phase1-reference-v1"}


@pytest.mark.parametrize(
    ("filename", "label", "confidence"),
    [
        ("leaf-01.jpg", "angular_leaf_spot", 0.501635),
        ("leaf-11.jpg", "bean_rust", 0.536608),
    ],
)
def test_prediction_returns_expected_contract(client, filename, label, confidence):
    sample = SAMPLES / filename
    response = client.post(
        "/predict", files={"file": (sample.name, sample.read_bytes(), "image/jpeg")}
    )
    assert response.status_code == 200
    result = response.json()
    assert set(result) == {"label", "confidence", "model_version"}
    assert result["label"] == label
    assert isinstance(result["confidence"], float)
    assert result["confidence"] == pytest.approx(confidence, abs=0.001)
    assert result["model_version"] == client.get("/ready").json()["model_version"]


def test_bad_image_is_rejected(client):
    response = client.post(
        "/predict", files={"file": ("bad.jpg", b"This is plain text.", "image/jpeg")}
    )
    assert response.status_code == 415
    assert response.json() == {"detail": "Upload a valid JPEG or PNG image."}


def test_missing_file_is_rejected(client):
    assert client.post("/predict").status_code == 422


def test_large_upload_is_rejected(client):
    content = b"0" * (service.MAX_UPLOAD_BYTES + 1)
    response = client.post(
        "/predict", files={"file": ("large.jpg", content, "image/jpeg")}
    )
    assert response.status_code == 413


def test_missing_model_keeps_service_live_but_unready(monkeypatch):
    def missing_model():
        raise FileNotFoundError("Model file missing")

    monkeypatch.setattr(service, "load_model", missing_model)
    with TestClient(service.app) as test_client:
        assert test_client.get("/health").status_code == 200
        assert test_client.get("/ready").status_code == 503
        response = test_client.post(
            "/predict", files={"file": ("image.jpg", b"image", "image/jpeg")}
        )
        assert response.status_code == 503
