"""Skip markers for tests that need a live dependency.

CI always provides PostgreSQL (with PostGIS) and Redis, so these tests always
run there. Locally they run as soon as `docker compose up -d db redis` is up,
and skip with an explanation otherwise, so `pytest` is still useful without the
stack running.
"""
from __future__ import annotations

import os

import pytest


def test_database_url() -> str:
    return os.environ.get(
        "TEST_DATABASE_URL",
        os.environ.get("DATABASE_URL", "postgresql+psycopg://app:app@localhost:5432/app"),
    )


def test_redis_url() -> str:
    return os.environ.get("REDIS_URL", "redis://localhost:6379/0")


def _database_available() -> bool:
    try:
        from sqlalchemy import create_engine, text

        engine = create_engine(test_database_url(), pool_pre_ping=True)
        with engine.connect() as connection:
            connection.execute(text("SELECT 1"))
        engine.dispose()
    except Exception:
        return False
    return True


def _redis_available() -> bool:
    try:
        import redis

        client = redis.Redis.from_url(test_redis_url(), socket_connect_timeout=1)
        client.ping()
        client.close()
    except Exception:
        return False
    return True


DATABASE_AVAILABLE = _database_available()
REDIS_AVAILABLE = _redis_available()

requires_database = pytest.mark.skipif(
    not DATABASE_AVAILABLE,
    reason=(
        "No PostgreSQL reachable. Run `docker compose up -d db`, apply "
        "`alembic upgrade head`, or set TEST_DATABASE_URL. CI always runs these."
    ),
)

requires_redis = pytest.mark.skipif(
    not REDIS_AVAILABLE,
    reason="No Redis reachable. Run `docker compose up -d redis` or set REDIS_URL. CI always runs these.",
)
