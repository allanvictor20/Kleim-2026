"""Redis client (M0).

Async client: the only M0 consumer is the idempotency middleware, which runs in
the ASGI layer. Later modules use it for rate limits (M1) and pub/sub (M8).
"""
from __future__ import annotations

from redis.asyncio import Redis

from app.core.config import get_settings

_client: Redis | None = None


def get_redis() -> Redis:
    """Process-wide client. Redis multiplexes, so one connection pool is right."""
    global _client
    if _client is None:
        _client = Redis.from_url(
            get_settings().redis_url, encoding="utf-8", decode_responses=False
        )
    return _client


async def check_redis() -> None:
    """Raise if Redis cannot answer. Used by /health/ready."""
    await get_redis().ping()


async def close_redis() -> None:
    global _client
    if _client is not None:
        await _client.aclose()
        _client = None
