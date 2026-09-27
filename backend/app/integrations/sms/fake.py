"""Console SMS adapter (M0).

In development OTP codes are not sent by SMS: they are logged, as the README
promises (`docker compose logs -f api`), and kept in an in-memory outbox that
tests assert against.
"""
from __future__ import annotations

import logging

from app.core.logging import mask_phone
from app.integrations.sms.interface import SentMessage

logger = logging.getLogger("kleim.sms")


class ConsoleSmsClient:
    def __init__(self) -> None:
        self.outbox: list[SentMessage] = []

    def send(self, to: str, body: str) -> SentMessage:
        message = SentMessage(to=to, body=body, reference=f"console-{len(self.outbox) + 1}")
        self.outbox.append(message)
        # The body carries the OTP, so this line is development-only: the phone
        # number is masked and the provider is `console`.
        logger.info("SMS (not sent) to %s: %s", mask_phone(to), body)
        return message

    def clear(self) -> None:
        self.outbox.clear()
