"""Africa's Talking SMS adapter. Implemented in M1 against the sandbox."""
from __future__ import annotations

from app.integrations.sms.interface import SentMessage


class AfricasTalkingSmsClient:
    def __init__(self, username: str, api_key: str) -> None:
        if not username or not api_key:
            raise ValueError("AFRICASTALKING_USERNAME and AFRICASTALKING_API_KEY are required")
        self._username = username
        self._api_key = api_key

    def send(self, to: str, body: str) -> SentMessage:
        raise NotImplementedError("Africa's Talking adapter is implemented in M1")
