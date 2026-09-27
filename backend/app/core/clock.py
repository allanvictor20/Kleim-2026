"""Single source of time (M0).

Never call `datetime.now()` elsewhere: services read the clock through `now()`
so tests can freeze time without patching the standard library
(CONTRIBUTING.md section 5).
"""
from __future__ import annotations

from collections.abc import Callable, Iterator
from contextlib import contextmanager
from datetime import UTC, datetime, timedelta

_override: datetime | None = None


def now() -> datetime:
    """Current time as a timezone-aware UTC datetime."""
    if _override is not None:
        return _override
    return datetime.now(UTC)


def today() -> datetime:
    """Midnight UTC of the current day."""
    current = now()
    return current.replace(hour=0, minute=0, second=0, microsecond=0)


def in_minutes(minutes: int) -> datetime:
    return now() + timedelta(minutes=minutes)


def in_seconds(seconds: int) -> datetime:
    return now() + timedelta(seconds=seconds)


@contextmanager
def frozen(at: datetime) -> Iterator[Callable[[timedelta], None]]:
    """Freeze `now()` at `at` for the duration of the block.

    Yields an `advance(delta)` callable so a test can step time forward, which
    is how the background-job tests in later modules exercise timeouts.
    """
    global _override
    if at.tzinfo is None:
        raise ValueError("frozen() requires a timezone-aware datetime")
    previous = _override
    _override = at

    def advance(delta: timedelta) -> None:
        global _override
        assert _override is not None
        _override = _override + delta

    try:
        yield advance
    finally:
        _override = previous
