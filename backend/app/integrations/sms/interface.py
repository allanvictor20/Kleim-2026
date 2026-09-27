"""SMS adapter interface (M0). Used for OTP delivery from M1."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol


@dataclass(frozen=True)
class SentMessage:
    to: str
    body: str
    reference: str | None = None


class SmsClient(Protocol):
    def send(self, to: str, body: str) -> SentMessage:
        """Send one message. `to` is E.164, e.g. +256700000001."""
        ...
