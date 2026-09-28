"""fee_configs reader (ADM-04, M0).

Fees, commission and timers are configuration, not constants: a service reads
them from here so operations can change a fee without a deploy (Implementation
Plan section 3.3). The row that applies is the newest one for a key whose
`effective_from` is not in the future, so a change can be scheduled and an old
order can still be explained by the values that were live when it was placed.
"""
from __future__ import annotations

from datetime import datetime
from typing import Any

from sqlalchemy import text
from sqlalchemy.orm import Session

from app.core.clock import now
from app.core.errors import AppError

BASIS_POINTS = 10_000


class ConfigMissing(AppError):
    code = "CONFIG_MISSING"
    status_code = 500
    message = "A required configuration value is missing"


_QUERY = text(
    """
    SELECT value
    FROM fee_configs
    WHERE key = :key AND effective_from <= :at
    ORDER BY effective_from DESC
    LIMIT 1
    """
)


def get_value(session: Session, key: str, at: datetime | None = None) -> Any:
    """Return the configured value for `key`, or raise `ConfigMissing`."""
    row = session.execute(_QUERY, {"key": key, "at": at or now()}).scalar_one_or_none()
    if row is None:
        raise ConfigMissing(f"No fee_configs row for {key!r}", details={"key": key})
    return row


def get_int(session: Session, key: str, at: datetime | None = None) -> int:
    value = get_value(session, key, at)
    if isinstance(value, bool) or not isinstance(value, int):
        raise ConfigMissing(f"fee_configs {key!r} is not an integer", details={"key": key})
    return value


def apply_rate(amount: int, rate_bps: int) -> int:
    """Apply a basis-point rate to an integer UGX amount, rounding half up.

    Kept here so commission (M6), rider share (M7) and ledger splits (M9) round
    the same way and always sum back to the original amount.
    """
    return (amount * rate_bps + BASIS_POINTS // 2) // BASIS_POINTS
