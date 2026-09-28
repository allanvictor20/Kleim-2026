"""Idempotency-Key middleware (NFR-11, M0).

Order creation and payment requests declare `Idempotency-Key` as a required
UUID header in `docs/api/openapi.yaml`. A retry over a flaky mobile connection
must not create a second order, so the first response for a key is stored in
Redis for 24 hours and replayed verbatim.

The key is scoped by caller, method and path: two customers may legitimately
generate the same client-side UUID, and a key must not leak one caller's
response to another. While the first request is still running, a duplicate gets
409 rather than a second execution.
"""
from __future__ import annotations

import hashlib
import json
import logging
from base64 import b64decode, b64encode
from collections.abc import AsyncIterator, Awaitable, Callable

from redis.asyncio import Redis
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response

from app.core.config import get_settings
from app.core.errors import error_body
from app.core.redis import get_redis

logger = logging.getLogger(__name__)

HEADER = "Idempotency-Key"
REPLAYED_HEADER = "Idempotency-Replayed"
_IDEMPOTENT_METHODS = frozenset({"POST", "PATCH", "PUT", "DELETE"})
_LOCK_TTL_SECONDS = 60
_PASSTHROUGH = "__in_progress__"
_COPIED_HEADERS = ("content-type", "location")

Handler = Callable[[Request], Awaitable[Response]]


def _cache_key(request: Request, key: str) -> str:
    """Namespace the key by caller, method and path."""
    caller = request.headers.get("authorization", "anonymous")
    digest = hashlib.sha256(
        "|".join([caller, request.method, request.url.path, key]).encode()
    ).hexdigest()
    return f"idempotency:{digest}"


class IdempotencyMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next: Handler) -> Response:
        key = request.headers.get(HEADER, "").strip()
        if not key or request.method not in _IDEMPOTENT_METHODS:
            return await call_next(request)

        redis = get_redis()
        cache_key = _cache_key(request, key)
        ttl = get_settings().idempotency_ttl_seconds

        try:
            claimed = await redis.set(cache_key, _PASSTHROUGH, nx=True, ex=_LOCK_TTL_SECONDS)
            if not claimed:
                stored = await redis.get(cache_key)
                if stored is not None and stored != _PASSTHROUGH.encode():
                    return _replay(stored)
                return _in_progress()
        except Exception:
            # Redis being down must not take the API down; log and run normally.
            logger.exception("idempotency store unavailable; processing without replay")
            return await call_next(request)

        try:
            response = await call_next(request)
        except Exception:
            await _release(redis, cache_key)
            raise

        if response.status_code >= 500:
            # A server error is not a settled outcome; let the client retry.
            await _release(redis, cache_key)
            return response

        body = await _read_body(response)
        await _store(redis, cache_key, response, body, ttl)
        return Response(
            content=body,
            status_code=response.status_code,
            headers=dict(response.headers),
            media_type=response.media_type,
        )


async def _read_body(response: Response) -> bytes:
    """Drain the downstream response so it can be both cached and returned.

    `call_next` hands back a streaming response, so the body has to be collected
    before it can be stored; the returned response is rebuilt from these bytes.
    """
    iterator: AsyncIterator[bytes | memoryview | str] | None = getattr(
        response, "body_iterator", None
    )
    if iterator is None:
        return bytes(response.body)
    chunks: list[bytes] = []
    async for chunk in iterator:
        chunks.append(chunk.encode() if isinstance(chunk, str) else bytes(chunk))
    return b"".join(chunks)


async def _store(
    redis: Redis, cache_key: str, response: Response, body: bytes, ttl: int
) -> None:
    record = {
        "status": response.status_code,
        "headers": {
            name: response.headers[name] for name in _COPIED_HEADERS if name in response.headers
        },
        "body": b64encode(body).decode(),
    }
    try:
        await redis.set(cache_key, json.dumps(record), ex=ttl)
    except Exception:
        logger.exception("could not store idempotent response")


async def _release(redis: Redis, cache_key: str) -> None:
    try:
        await redis.delete(cache_key)
    except Exception:
        logger.exception("could not release idempotency lock")


def _replay(stored: bytes) -> Response:
    record = json.loads(stored)
    headers = dict(record.get("headers", {}))
    headers[REPLAYED_HEADER] = "true"
    return Response(
        content=b64decode(record["body"]),
        status_code=record["status"],
        headers=headers,
    )


def _in_progress() -> Response:
    body = error_body(
        "IDEMPOTENCY_IN_PROGRESS",
        "An identical request is still being processed; retry shortly",
    )
    return Response(
        content=json.dumps(body),
        status_code=409,
        media_type="application/json",
        headers={"Retry-After": "2"},
    )
