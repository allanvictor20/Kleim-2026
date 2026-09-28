"""Database engine, session and declarative base (M0).

The naming convention here is what makes Alembic autogenerate produce stable
index and constraint names, so migrations stay reviewable.
"""
from __future__ import annotations

import uuid
from collections.abc import Iterator
from functools import lru_cache
from typing import Any

from sqlalchemy import MetaData, create_engine
from sqlalchemy.engine import Engine
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker

from app.core.config import get_settings

NAMING_CONVENTION: dict[str, str] = {
    "ix": "ix_%(column_0_label)s",
    "uq": "uq_%(table_name)s_%(column_0_name)s",
    "ck": "ck_%(table_name)s_%(constraint_name)s",
    "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
    "pk": "pk_%(table_name)s",
}


class Base(DeclarativeBase):
    """Declarative base shared by every module's models."""

    metadata = MetaData(naming_convention=NAMING_CONVENTION)


def new_uuid() -> uuid.UUID:
    """Application-side primary key, so a service knows the id before flush."""
    return uuid.uuid4()


@lru_cache(maxsize=1)
def get_engine() -> Engine:
    settings = get_settings()
    return create_engine(
        settings.database_url,
        pool_pre_ping=True,
        future=True,
        echo=False,
    )


@lru_cache(maxsize=1)
def get_sessionmaker() -> sessionmaker[Session]:
    return sessionmaker(bind=get_engine(), autoflush=False, expire_on_commit=False)


def get_session() -> Iterator[Session]:
    """FastAPI dependency: one session per request, rolled back on failure."""
    session = get_sessionmaker()()
    try:
        yield session
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()


def check_database() -> None:
    """Raise if the database cannot answer. Used by /health/ready."""
    from sqlalchemy import text

    with get_engine().connect() as connection:
        connection.execute(text("SELECT 1"))


def dispose_engine() -> None:
    """Close pooled connections on shutdown."""
    if get_engine.cache_info().currsize:
        get_engine().dispose()


def reset_engine_cache() -> None:
    """Drop cached engine and sessionmaker; used by tests that repoint the URL."""
    dispose_engine()
    get_engine.cache_clear()
    get_sessionmaker.cache_clear()


def json_column_type() -> Any:
    """JSONB on PostgreSQL. Kept in one place so models do not import the dialect."""
    from sqlalchemy.dialects.postgresql import JSONB

    return JSONB
