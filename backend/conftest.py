"""Shared fixtures: test database (PostGIS container), API client, factories, controlled clock.

This file sits at the backend root, not under `tests/`, so the per-module suites
in `app/<module>/tests/` share the same fixtures -- `pyproject.toml` collects
both trees (`testpaths = ["tests", "app"]`).
"""
from __future__ import annotations

from collections.abc import Iterator
from datetime import UTC, datetime

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.engine import Engine
from sqlalchemy.orm import Session, sessionmaker

from app.core import clock, events
from app.core.config import Settings, get_settings
from tests.markers import DATABASE_AVAILABLE, test_database_url, test_redis_url

# A fixed instant for deterministic assertions: a Tuesday afternoon in Kampala.
FROZEN_NOW = datetime(2026, 3, 10, 12, 0, 0, tzinfo=UTC)


@pytest.fixture(scope="session")
def settings() -> Settings:
    get_settings.cache_clear()
    return Settings(
        app_env="test",
        database_url=test_database_url(),
        redis_url=test_redis_url(),
        jwt_secret="test-only-secret-long-enough-for-hs256",
        sms_provider="console",
        payment_provider="simulated",
        maps_provider="osm",
    )


@pytest.fixture
def app(settings: Settings) -> FastAPI:
    from app.main import create_app

    return create_app(settings)


@pytest.fixture
def client(app: FastAPI) -> Iterator[TestClient]:
    """Requests go through the real middleware stack, so tests exercise the
    request-id and error-shape behaviour rather than a stripped-down app."""
    with TestClient(app, raise_server_exceptions=False) as test_client:
        yield test_client


@pytest.fixture(scope="session")
def engine() -> Iterator[Engine]:
    if not DATABASE_AVAILABLE:
        pytest.skip("no database")
    created = create_engine(test_database_url(), pool_pre_ping=True)
    yield created
    created.dispose()


@pytest.fixture
def session(engine: Engine) -> Iterator[Session]:
    """One transaction per test, always rolled back, so tests never leak rows.

    The outer transaction also lets a test insert into an append-only table and
    then discard the row.
    """
    connection = engine.connect()
    transaction = connection.begin()
    maker = sessionmaker(bind=connection, autoflush=False, expire_on_commit=False)
    db = maker()
    try:
        yield db
    finally:
        db.close()
        transaction.rollback()
        connection.close()


@pytest.fixture
def frozen_clock() -> Iterator[None]:
    """Freeze `app.core.clock.now()`; later modules step it to test timeouts."""
    with clock.frozen(FROZEN_NOW):
        yield


@pytest.fixture(autouse=True)
def clean_event_bus() -> Iterator[None]:
    """Subscribers registered by one test must not leak into the next."""
    events.bus.clear()
    yield
    events.bus.clear()
