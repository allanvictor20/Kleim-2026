"""In-process domain event bus (M0).

Modules must not query another module's tables (SDD section 10), so they talk
through service calls or the events published here -- `order.accepted`,
`payment.succeeded` and so on from M5 onward.

Handlers are synchronous and must be quick: a handler that needs to send an SMS
or call an external service enqueues an ARQ job instead of doing the work
inline. A failing handler is logged and never propagates, so one subscriber
cannot roll back the publisher's transaction.
"""
from __future__ import annotations

import logging
from collections import defaultdict
from collections.abc import Callable
from typing import Any, TypeVar

logger = logging.getLogger(__name__)

Handler = Callable[[dict[str, Any]], None]
H = TypeVar("H", bound=Handler)


class EventBus:
    def __init__(self) -> None:
        self._handlers: dict[str, list[Handler]] = defaultdict(list)

    def subscribe(self, event_name: str) -> Callable[[H], H]:
        """Decorator registering a handler for one event name."""

        def decorator(handler: H) -> H:
            self._handlers[event_name].append(handler)
            return handler

        return decorator

    def register(self, event_name: str, handler: Handler) -> None:
        self._handlers[event_name].append(handler)

    def publish(self, event_name: str, payload: dict[str, Any] | None = None) -> None:
        """Call every handler for `event_name`, isolating failures."""
        data = payload or {}
        handlers = self._handlers.get(event_name, [])
        logger.info(
            "event published", extra={"event": event_name, "subscribers": len(handlers)}
        )
        for handler in handlers:
            try:
                handler(data)
            except Exception:
                logger.exception(
                    "event handler failed",
                    extra={"event": event_name, "handler": getattr(handler, "__qualname__", "?")},
                )

    def handlers_for(self, event_name: str) -> tuple[Handler, ...]:
        return tuple(self._handlers.get(event_name, []))

    def clear(self) -> None:
        """Drop every subscriber. Tests only."""
        self._handlers.clear()


bus = EventBus()


def subscribe(event_name: str) -> Callable[[H], H]:
    """Module-level shorthand for `bus.subscribe`."""
    return bus.subscribe(event_name)


def publish(event_name: str, payload: dict[str, Any] | None = None) -> None:
    """Module-level shorthand for `bus.publish`."""
    bus.publish(event_name, payload)
