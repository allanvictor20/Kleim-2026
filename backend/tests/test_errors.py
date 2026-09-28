"""Every error leaving the API uses the SDD section 15.1 envelope."""
from __future__ import annotations

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from pydantic import BaseModel

from app.core.errors import (
    BusinessRuleError,
    Forbidden,
    NotFound,
    RateLimited,
    Unauthorized,
    ValidationError,
)
from app.core.middleware import HEADER


class Body(BaseModel):
    quantity: int


@pytest.fixture
def error_app(app: FastAPI) -> FastAPI:
    @app.get("/boom/not-found")
    def not_found() -> None:
        raise NotFound("No such order")

    @app.get("/boom/forbidden")
    def forbidden() -> None:
        raise Forbidden()

    @app.get("/boom/rule")
    def rule() -> None:
        raise BusinessRuleError(
            "Selected size is no longer available",
            code="OUT_OF_STOCK",
            details={"variant_id": "abc"},
        )

    @app.get("/boom/rate-limited")
    def rate_limited() -> None:
        raise RateLimited("Try again shortly", retry_after_seconds=42)

    @app.get("/boom/unhandled")
    def unhandled() -> None:
        raise RuntimeError("something the code did not expect")

    @app.post("/boom/validate")
    def validate(body: Body) -> dict[str, int]:
        return {"quantity": body.quantity}

    return app


def test_domain_error_shape(error_app: FastAPI) -> None:
    with TestClient(error_app, raise_server_exceptions=False) as client:
        response = client.get("/boom/not-found")

    assert response.status_code == 404
    error = response.json()["error"]
    assert error["code"] == "NOT_FOUND"
    assert error["message"] == "No such order"
    assert error["request_id"]


def test_every_error_carries_code_message_and_request_id(error_app: FastAPI) -> None:
    paths = ["/boom/not-found", "/boom/forbidden", "/boom/rule", "/boom/unhandled"]
    with TestClient(error_app, raise_server_exceptions=False) as client:
        for path in paths:
            body = client.get(path).json()
            assert set(body) == {"error"}, path
            assert {"code", "message", "request_id"} <= set(body["error"]), path


def test_business_rule_error_keeps_its_catalogue_code(error_app: FastAPI) -> None:
    with TestClient(error_app, raise_server_exceptions=False) as client:
        response = client.get("/boom/rule")

    assert response.status_code == 409
    assert response.json()["error"]["code"] == "OUT_OF_STOCK"
    assert response.json()["error"]["details"] == {"variant_id": "abc"}


def test_rate_limited_sets_retry_after(error_app: FastAPI) -> None:
    with TestClient(error_app, raise_server_exceptions=False) as client:
        response = client.get("/boom/rate-limited")

    assert response.status_code == 429
    assert response.headers["Retry-After"] == "42"
    assert response.json()["error"]["code"] == "RATE_LIMITED"


def test_unhandled_error_does_not_leak_the_exception(error_app: FastAPI) -> None:
    with TestClient(error_app, raise_server_exceptions=False) as client:
        response = client.get("/boom/unhandled")

    assert response.status_code == 500
    error = response.json()["error"]
    assert error["code"] == "INTERNAL_ERROR"
    assert "something the code did not expect" not in error["message"]


def test_request_validation_is_wrapped(error_app: FastAPI) -> None:
    with TestClient(error_app, raise_server_exceptions=False) as client:
        response = client.post("/boom/validate", json={"quantity": "many"})

    assert response.status_code == 422
    error = response.json()["error"]
    assert error["code"] == "VALIDATION_ERROR"
    assert error["details"]["fields"][0]["field"] == "quantity"


def test_unknown_route_uses_the_same_shape(client: TestClient) -> None:
    body = client.get("/no-such-path").json()
    assert body["error"]["code"] == "NOT_FOUND"


def test_request_id_is_echoed_and_reused(client: TestClient) -> None:
    generated = client.get("/health/live")
    assert generated.headers[HEADER]

    supplied = client.get("/health/live", headers={HEADER: "trace-from-proxy"})
    assert supplied.headers[HEADER] == "trace-from-proxy"


def test_validation_error_class_defaults() -> None:
    assert ValidationError().code == "VALIDATION_ERROR"
    assert Unauthorized().status_code == 401
