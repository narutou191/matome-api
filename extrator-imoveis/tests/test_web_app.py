import io
from unittest.mock import patch

from fastapi.testclient import TestClient

from web.app import app

client = TestClient(app)


def _fake_image(name):
    return (name, io.BytesIO(b"fake-bytes"), "image/png")


@patch("web.app.process_property", return_value="🏠 resultado de teste")
def test_process_returns_formatted_result(mock_process):
    response = client.post(
        "/api/process",
        files=[
            ("images", _fake_image("foto1.png")),
            ("images", _fake_image("foto2.png")),
        ],
    )

    assert response.status_code == 200
    assert response.json() == {"result": "🏠 resultado de teste"}
    mock_process.assert_called_once()


def test_process_rejects_wrong_image_count():
    response = client.post("/api/process", files=[("images", _fake_image("foto1.png"))])

    assert response.status_code == 400
    assert "2 capturas" in response.json()["detail"]


def test_process_rejects_invalid_image_format():
    response = client.post(
        "/api/process",
        files=[
            ("images", _fake_image("foto1.png")),
            ("images", ("foto2.heic", io.BytesIO(b"fake-bytes"), "image/heic")),
        ],
    )

    assert response.status_code == 400
    assert response.json()["detail"] == "Formato inválido. Use PNG, JPG ou WebP"


def test_health_check():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}
