"""Choose the push adapter from settings (M0)."""
from __future__ import annotations

from functools import lru_cache

from app.core.config import get_settings
from app.integrations.push.fake import InMemoryPushClient
from app.integrations.push.interface import PushClient


@lru_cache(maxsize=1)
def get_push_client() -> PushClient:
    settings = get_settings()
    if not settings.fcm_credentials_json:
        return InMemoryPushClient()
    raise NotImplementedError("Firebase Cloud Messaging adapter is implemented in M8")


def reset_push_client() -> None:
    get_push_client.cache_clear()
