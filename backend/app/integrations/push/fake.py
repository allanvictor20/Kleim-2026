"""In-memory push adapter (M0)."""
from __future__ import annotations

import logging

from app.integrations.push.interface import PushMessage

logger = logging.getLogger("kleim.push")


class InMemoryPushClient:
    def __init__(self) -> None:
        self.sent: list[PushMessage] = []

    def send(self, message: PushMessage) -> bool:
        self.sent.append(message)
        logger.info("push (not sent)", extra={"title": message.title})
        return True

    def clear(self) -> None:
        self.sent.clear()
