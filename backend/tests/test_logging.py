"""Customer phone numbers and addresses must never reach a log line
(CONTRIBUTING.md section 9)."""
from __future__ import annotations

import json
import logging

from app.core.context import set_request_id
from app.core.logging import JsonFormatter, mask_address, mask_phone


def test_phone_is_masked_but_still_recognisable() -> None:
    masked = mask_phone("+256700000001")
    assert masked.startswith("+2567")
    assert masked.endswith("0001")
    assert "70000000" not in masked


def test_short_or_missing_phone_is_fully_hidden() -> None:
    assert mask_phone(None) == "-"
    assert set(mask_phone("0700")) == {"*"}


def test_address_keeps_only_a_coarse_area() -> None:
    masked = mask_address("Plot 14 Kira Road, Kamwokya, near the blue gate")
    assert "Kamwokya" not in masked
    assert "blue gate" not in masked


def test_log_lines_are_json_and_carry_the_request_id() -> None:
    set_request_id("req-123")
    record = logging.LogRecord(
        name="kleim.test",
        level=logging.INFO,
        pathname=__file__,
        lineno=1,
        msg="order accepted %s",
        args=("o-1",),
        exc_info=None,
    )
    record.order_id = "o-1"

    payload = json.loads(JsonFormatter().format(record))

    assert payload["message"] == "order accepted o-1"
    assert payload["request_id"] == "req-123"
    assert payload["level"] == "INFO"
    assert payload["order_id"] == "o-1"
