"""The event bus is how modules talk without touching each other's tables."""
from __future__ import annotations

from typing import Any

from app.core import events


def test_subscriber_receives_the_payload() -> None:
    seen: list[dict[str, Any]] = []

    @events.subscribe("order.accepted")
    def handler(payload: dict[str, Any]) -> None:
        seen.append(payload)

    events.publish("order.accepted", {"order_id": "o-1"})

    assert seen == [{"order_id": "o-1"}]


def test_every_subscriber_is_called_in_registration_order() -> None:
    calls: list[str] = []
    events.bus.register("order.accepted", lambda _: calls.append("first"))
    events.bus.register("order.accepted", lambda _: calls.append("second"))

    events.publish("order.accepted")

    assert calls == ["first", "second"]


def test_a_failing_handler_does_not_stop_the_others_or_the_publisher() -> None:
    """A notification failure must never roll back an accepted order."""
    calls: list[str] = []

    def explodes(payload: dict[str, Any]) -> None:
        raise RuntimeError("SMS provider down")

    events.bus.register("order.accepted", explodes)
    events.bus.register("order.accepted", lambda _: calls.append("still ran"))

    events.publish("order.accepted", {"order_id": "o-1"})

    assert calls == ["still ran"]


def test_publishing_an_unsubscribed_event_is_harmless() -> None:
    events.publish("nobody.listens", {"a": 1})


def test_payload_defaults_to_empty() -> None:
    seen: list[dict[str, Any]] = []
    events.bus.register("order.expired", seen.append)

    events.publish("order.expired")

    assert seen == [{}]
