"""The four apps run on their own ports, so the API must allow their origins.

Without this the M0 exit criterion cannot be met: a browser blocks the request
before the API ever sees it (found by loading the built shells against a running
API, not by a unit test).
"""
from __future__ import annotations

from fastapi.testclient import TestClient

from app.core.middleware import HEADER as REQUEST_ID_HEADER

CUSTOMER_APP = "http://localhost:5173"


def test_customer_app_origin_is_allowed(client: TestClient) -> None:
    response = client.get("/health/live", headers={"Origin": CUSTOMER_APP})

    assert response.headers["access-control-allow-origin"] == CUSTOMER_APP


def test_every_app_port_is_allowed(client: TestClient) -> None:
    for port in (5173, 5174, 5175, 5176):
        origin = f"http://localhost:{port}"
        response = client.get("/health/live", headers={"Origin": origin})
        assert response.headers.get("access-control-allow-origin") == origin, origin


def test_an_unknown_origin_is_not_allowed(client: TestClient) -> None:
    """A phishing page must not be able to read a signed-in customer's data."""
    response = client.get("/health/live", headers={"Origin": "https://not-kleim.example"})

    assert "access-control-allow-origin" not in response.headers


def test_preflight_permits_the_headers_the_client_sends(client: TestClient) -> None:
    response = client.options(
        "/health/live",
        headers={
            "Origin": CUSTOMER_APP,
            "Access-Control-Request-Method": "POST",
            "Access-Control-Request-Headers": "authorization,content-type,idempotency-key",
        },
    )

    assert response.status_code == 200
    allowed = response.headers["access-control-allow-headers"].lower()
    for header in ("authorization", "content-type", "idempotency-key"):
        assert header in allowed


def test_request_id_is_readable_by_the_browser(client: TestClient) -> None:
    """A bug report is only traceable if the page can read the request id."""
    response = client.get("/health/live", headers={"Origin": CUSTOMER_APP})

    exposed = response.headers.get("access-control-expose-headers", "").lower()
    assert REQUEST_ID_HEADER.lower() in exposed


def test_origins_can_be_configured_as_a_comma_separated_string() -> None:
    """`.env` carries a list as one line, which pydantic would otherwise reject."""
    from app.core.config import Settings

    settings = Settings(cors_origins="https://kleim.example, https://admin.kleim.example")  # type: ignore[arg-type]

    assert settings.cors_origins == ["https://kleim.example", "https://admin.kleim.example"]
