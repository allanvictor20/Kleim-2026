"""Push notification interface (M0). Firebase Cloud Messaging arrives in M8."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Protocol


@dataclass(frozen=True)
class PushMessage:
    token: str
    title: str
    body: str
    data: dict[str, str] = field(default_factory=dict)


class PushClient(Protocol):
    def send(self, message: PushMessage) -> bool:
        """Return False for a token the provider rejected as stale."""
        ...
