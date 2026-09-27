"""Services read time through the clock so tests can control it."""
from __future__ import annotations

from datetime import UTC, datetime, timedelta

import pytest

from app.core import clock


def test_now_is_timezone_aware_utc() -> None:
    assert clock.now().tzinfo is not None
    assert clock.now().utcoffset() == timedelta(0)


def test_frozen_holds_time_still_and_can_advance_it() -> None:
    at = datetime(2026, 3, 10, 12, 0, tzinfo=UTC)

    with clock.frozen(at) as advance:
        assert clock.now() == at
        advance(timedelta(minutes=11))
        assert clock.now() == at + timedelta(minutes=11)


def test_frozen_restores_the_real_clock_afterwards() -> None:
    at = datetime(2026, 3, 10, 12, 0, tzinfo=UTC)
    with clock.frozen(at):
        pass
    assert clock.now() != at


def test_frozen_refuses_a_naive_datetime() -> None:
    with pytest.raises(ValueError, match="timezone-aware"), clock.frozen(datetime(2026, 3, 10, 12, 0)):
        pass


def test_helpers_are_relative_to_the_frozen_now() -> None:
    at = datetime(2026, 3, 10, 12, 0, tzinfo=UTC)
    with clock.frozen(at):
        assert clock.in_minutes(10) == at + timedelta(minutes=10)
        assert clock.in_seconds(45) == at + timedelta(seconds=45)
