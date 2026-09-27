"""Fees, commission and timers are configuration, never constants (ADM-04)."""
from __future__ import annotations

import pytest
from sqlalchemy.orm import Session

from app.core.settings_store import ConfigMissing, apply_rate, get_int, get_value
from tests.markers import requires_database


def test_apply_rate_rounds_half_up_and_stays_integer() -> None:
    # 12% commission on UGX 100,000 of clothes.
    assert apply_rate(100_000, 1200) == 12_000
    # Rounding is explicit, so a split always sums back to the whole amount.
    assert apply_rate(4_500, 8000) == 3_600
    assert apply_rate(1, 5000) == 1
    assert isinstance(apply_rate(33_333, 1200), int)


def test_apply_rate_of_zero_is_zero() -> None:
    assert apply_rate(0, 1200) == 0
    assert apply_rate(50_000, 0) == 0


@requires_database
def test_seeded_values_match_the_sdd(session: Session) -> None:
    assert get_int(session, "delivery.base_fee") == 2500
    assert get_int(session, "delivery.per_km") == 1000
    assert get_int(session, "delivery.min_fee") == 3000
    assert get_int(session, "delivery.max_fee") == 15000
    assert get_int(session, "delivery.rounding") == 500
    assert get_int(session, "commission.rate_bps") == 1200
    assert get_int(session, "delivery.rider_share_bps") == 8000
    assert get_int(session, "timers.seller_response_minutes") == 10
    assert get_int(session, "timers.payment_window_minutes") == 10
    assert get_int(session, "timers.rider_offer_seconds") == 45


@requires_database
def test_a_missing_key_is_a_loud_failure(session: Session) -> None:
    """Silently defaulting a fee would misprice an order."""
    with pytest.raises(ConfigMissing):
        get_value(session, "delivery.invented_fee")


@requires_database
def test_the_newest_effective_row_wins(session: Session) -> None:
    """Operations raise a fee by inserting a new row; history is preserved."""
    from sqlalchemy import text

    session.execute(
        text(
            "INSERT INTO fee_configs (id, key, value, effective_from) "
            "VALUES (gen_random_uuid(), 'delivery.base_fee', '3000', now())"
        )
    )
    session.flush()

    assert get_int(session, "delivery.base_fee") == 3000
