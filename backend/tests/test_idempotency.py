"""A retried request must not create a second order (NFR-11).

`docs/api/openapi.yaml` declares `Idempotency-Key` as a required UUID header on
order creation and payment requests: the same key within 24 hours returns the
original response.
"""
from __future__ import annotations

import uuid

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from starlette.requests import Request

from app.core.idempotency import HEADER, REPLAYED_HEADER, _cache_key
from app.core.redis import close_redis, get_redis
from tests.markers import requires_redis


@pytest.fixture
def counting_app(app: FastAPI) -> FastAPI:
    """An endpoint that reports how many times it actually ran."""
    state = {"calls": 0}

    @app.post("/orders-test")
    def create_order() -> dict[str, int]:
        state["calls"] += 1
        return {"calls": state["calls"], "order": 1}

    @app.post("/boom-test")
    def boom() -> dict[str, int]:
        state["calls"] += 1
        raise RuntimeError("provider timed out")

    app.state.calls = state
    return app


def _request(path: str = "/orders", auth: str = "Bearer a") -> Request:
    return Request(
        {
            "type": "http",
            "method": "POST",
            "path": path,
            "headers": [(b"authorization", auth.encode())],
            "query_string": b"",
        }
    )


def test_cache_key_is_scoped_to_caller_method_and_path() -> None:
    """Two customers may generate the same client-side UUID; neither may see the
    other's response."""
    key = str(uuid.uuid4())

    same = _cache_key(_request(), key) == _cache_key(_request(), key)
    other_caller = _cache_key(_request(auth="Bearer b"), key)
    other_path = _cache_key(_request(path="/payments"), key)

    assert same
    assert _cache_key(_request(), key) != other_caller
    assert _cache_key(_request(), key) != other_path


def test_a_different_key_is_a_different_request() -> None:
    assert _cache_key(_request(), "key-1") != _cache_key(_request(), "key-2")


@requires_redis
def test_repeated_key_returns_the_identical_response(counting_app: FastAPI) -> None:
    key = str(uuid.uuid4())
    headers = {HEADER: key, "Authorization": "Bearer test-token"}

    with TestClient(counting_app, raise_server_exceptions=False) as client:
        first = client.post("/orders-test", headers=headers)
        second = client.post("/orders-test", headers=headers)

    assert first.status_code == second.status_code
    assert first.json() == second.json()
    assert second.headers[REPLAYED_HEADER] == "true"
    # The decisive assertion: the handler ran once, so only one order exists.
    assert counting_app.state.calls["calls"] == 1


@requires_redis
def test_a_new_key_runs_the_handler_again(counting_app: FastAPI) -> None:
    with TestClient(counting_app, raise_server_exceptions=False) as client:
        client.post(
            "/orders-test",
            headers={HEADER: str(uuid.uuid4()), "Authorization": "Bearer test-token"},
        )
        client.post(
            "/orders-test",
            headers={HEADER: str(uuid.uuid4()), "Authorization": "Bearer test-token"},
        )

    assert counting_app.state.calls["calls"] == 2


@requires_redis
def test_no_key_means_no_caching(counting_app: FastAPI) -> None:
    with TestClient(counting_app, raise_server_exceptions=False) as client:
        client.post("/orders-test")
        client.post("/orders-test")

    assert counting_app.state.calls["calls"] == 2


@requires_redis
def test_a_failed_request_is_not_cached(counting_app: FastAPI) -> None:
    """A provider timeout is not a settled outcome: the client may retry."""
    key = str(uuid.uuid4())
    headers = {HEADER: key, "Authorization": "Bearer test-token"}

    with TestClient(counting_app, raise_server_exceptions=False) as client:
        first = client.post("/boom-test", headers=headers)
        second = client.post("/boom-test", headers=headers)

    assert first.status_code == 500
    assert second.status_code == 500
    assert counting_app.state.calls["calls"] == 2


@requires_redis
@pytest.mark.asyncio
async def test_stored_response_expires_within_a_day(counting_app: FastAPI) -> None:
    key = str(uuid.uuid4())
    headers = {HEADER: key, "Authorization": "Bearer test-token"}

    with TestClient(counting_app, raise_server_exceptions=False) as client:
        client.post("/orders-test", headers=headers)

    redis = get_redis()
    stored = [k async for k in redis.scan_iter(match="idempotency:*")]
    ttls = [await redis.ttl(k) for k in stored]
    await close_redis()

    assert ttls, "the response should have been stored"
    assert max(ttls) <= 60 * 60 * 24
