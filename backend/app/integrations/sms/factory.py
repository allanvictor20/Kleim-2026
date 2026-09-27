"""Choose the SMS adapter from settings (M0)."""
from __future__ import annotations

from functools import lru_cache

from app.core.config import get_settings
from app.integrations.sms.fake import ConsoleSmsClient
from app.integrations.sms.interface import SmsClient


@lru_cache(maxsize=1)
def get_sms_client() -> SmsClient:
    settings = get_settings()
    if settings.sms_provider == "console":
        return ConsoleSmsClient()
    if settings.sms_provider == "africastalking":
        from app.integrations.sms.africastalking import AfricasTalkingSmsClient

        return AfricasTalkingSmsClient(
            settings.africastalking_username, settings.africastalking_api_key
        )
    raise ValueError(f"Unknown SMS_PROVIDER: {settings.sms_provider}")


def reset_sms_client() -> None:
    get_sms_client.cache_clear()
