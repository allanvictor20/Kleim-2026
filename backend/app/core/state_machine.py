"""Generic state machine (M0).

Orders (M5) and deliveries (M7) share this helper. Nothing in the codebase
assigns a `status` attribute directly (CONTRIBUTING.md section 5): every change
goes through `transition`, which validates the edge, writes history and
publishes an event.
"""
from __future__ import annotations

from collections.abc import Callable, Mapping
from typing import Any, Protocol

from app.core import events
from app.core.errors import BusinessRuleError


class InvalidTransition(BusinessRuleError):
    code = "INVALID_TRANSITION"
    status_code = 409


class HasStatus(Protocol):
    status: str


HistoryWriter = Callable[[str, str, str | None, str | None], None]


class StateMachine:
    """Allowed edges for one entity type.

    `transitions` maps a current state to the states reachable from it. A state
    with an empty set is terminal.
    """

    def __init__(self, name: str, transitions: Mapping[str, frozenset[str] | set[str]]) -> None:
        self.name = name
        self._transitions: dict[str, frozenset[str]] = {
            state: frozenset(targets) for state, targets in transitions.items()
        }
        unknown = {
            target
            for targets in self._transitions.values()
            for target in targets
            if target not in self._transitions
        }
        if unknown:
            raise ValueError(
                f"{name}: transitions reference undeclared states {sorted(unknown)}"
            )

    @property
    def states(self) -> frozenset[str]:
        return frozenset(self._transitions)

    def is_terminal(self, state: str) -> bool:
        return not self._transitions.get(state, frozenset())

    def can(self, source: str, target: str) -> bool:
        return target in self._transitions.get(source, frozenset())

    def next_states(self, source: str) -> frozenset[str]:
        return self._transitions.get(source, frozenset())

    def assert_transition(self, source: str, target: str) -> None:
        """Raise `InvalidTransition` unless the edge is declared."""
        if source not in self._transitions:
            raise InvalidTransition(
                f"{self.name} has no state {source!r}",
                details={"entity": self.name, "from": source, "to": target},
            )
        if target not in self._transitions:
            raise InvalidTransition(
                f"{self.name} has no state {target!r}",
                details={"entity": self.name, "from": source, "to": target},
            )
        if not self.can(source, target):
            raise InvalidTransition(
                f"{self.name} cannot move from {source} to {target}",
                details={
                    "entity": self.name,
                    "from": source,
                    "to": target,
                    "allowed": sorted(self.next_states(source)),
                },
            )

    def transition(
        self,
        entity: HasStatus,
        target: str,
        *,
        actor_id: str | None = None,
        reason: str | None = None,
        history: HistoryWriter | None = None,
        event: str | None = None,
        event_payload: Mapping[str, Any] | None = None,
    ) -> str:
        """Move `entity` to `target`, recording history and emitting an event.

        Returns the previous state. The history writer receives
        `(from_state, to_state, actor_id, reason)` and is supplied by the owning
        module, which knows its own history table.
        """
        source = entity.status
        self.assert_transition(source, target)
        entity.status = target
        if history is not None:
            history(source, target, actor_id, reason)
        if event is not None:
            payload: dict[str, Any] = {
                "from": source,
                "to": target,
                "actor_id": actor_id,
                "reason": reason,
            }
            payload.update(event_payload or {})
            events.publish(event, payload)
        return source
