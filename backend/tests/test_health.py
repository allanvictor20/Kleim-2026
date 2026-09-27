from fastapi.testclient import TestClient

from app.main import app


def test_live() -> None:
    assert TestClient(app).get("/health/live").json() == {"status": "ok"}
