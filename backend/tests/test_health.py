from fastapi.testclient import TestClient

from app.main import app


def test_live() -> None:
    assert TestClient(app).get("/health/live").json() == {"status": "ok"}


def test_ready_reports_each_dependency(client: TestClient) -> None:
    """Ready must name what is wrong, and refuse traffic when anything is."""
    response = client.get("/health/ready")
    body = response.json()

    if response.status_code == 200:
        assert body == {"status": "ok", "checks": {"database": "ok", "redis": "ok"}}
        return

    # No database or Redis in this environment: the contract is a 503 carrying
    # the standard error envelope and saying which dependency failed.
    assert response.status_code == 503
    assert body["error"]["code"] == "SERVICE_UNAVAILABLE"
    assert set(body["error"]["details"]["checks"]) == {"database", "redis"}
