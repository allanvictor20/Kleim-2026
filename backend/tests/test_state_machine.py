"""The shared state machine is the only way a status changes (M5, M7 reuse it)."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

import pytest

from app.core import events
from app.core.state_machine import InvalidTransition, StateMachine

# A miniature version of the order lifecycle, enough to test the helper itself.
ORDER = StateMachine(
    "order",
    {
        "pending_seller": {"accepted", "rejected", "expired"},
        "accepted": {"ready", "cancelled"},
        "ready": {"delivered"},
        "rejected": set(),
        "expired": set(),
        "cancelled": set(),
        "delivered": set(),
    },
)


@dataclass
class FakeOrder:
    status: str = "pending_seller"
    history: list[tuple[str, str, str | None, str | None]] = field(default_factory=list)

    def record(self, source: str, target: str, actor: str | None, reason: str | None) -> None:
        self.history.append((source, target, actor, reason))


def test_declared_transition_is_allowed() -> None:
    assert ORDER.can("pending_seller", "accepted")
    ORDER.assert_transition("pending_seller", "accepted")


def test_undefined_transition_is_rejected() -> None:
    with pytest.raises(InvalidTransition) as raised:
        ORDER.assert_transition("pending_seller", "delivered")

    error = raised.value
    assert error.code == "INVALID_TRANSITION"
    assert error.status_code == 409
    assert error.details is not None
    assert error.details["allowed"] == ["accepted", "expired", "rejected"]


def test_unknown_state_is_rejected() -> None:
    with pytest.raises(InvalidTransition):
        ORDER.assert_transition("pending_seller", "refunded")
    with pytest.raises(InvalidTransition):
        ORDER.assert_transition("invented", "accepted")


def test_terminal_states_have_no_exit() -> None:
    assert ORDER.is_terminal("delivered")
    assert not ORDER.is_terminal("accepted")
    with pytest.raises(InvalidTransition):
        ORDER.assert_transition("delivered", "accepted")


def test_transition_writes_history_and_publishes() -> None:
    seen: list[dict[str, Any]] = []
    events.bus.register("order.accepted", seen.append)
    order = FakeOrder()

    previous = ORDER.transition(
        order,
        "accepted",
        actor_id="seller-1",
        reason="seller tapped accept",
        history=order.record,
        event="order.accepted",
        event_payload={"order_id": "o-1"},
    )

    assert previous == "pending_seller"
    assert order.status == "accepted"
    assert order.history == [("pending_seller", "accepted", "seller-1", "seller tapped accept")]
    assert seen == [
        {
            "from": "pending_seller",
            "to": "accepted",
            "actor_id": "seller-1",
            "reason": "seller tapped accept",
            "order_id": "o-1",
        }
    ]


def test_refused_transition_leaves_the_entity_untouched() -> None:
    order = FakeOrder(status="delivered")

    with pytest.raises(InvalidTransition):
        ORDER.transition(order, "accepted", history=order.record, event="order.accepted")

    assert order.status == "delivered"
    assert order.history == []


def test_machine_rejects_a_typo_in_its_own_definition() -> None:
    """A target state that is never declared is a bug in the table, not runtime."""
    with pytest.raises(ValueError, match="undeclared states"):
        StateMachine("broken", {"a": {"b"}})
