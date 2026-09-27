"""Choose the payments adapter from settings (M0). See ADR-003."""
from __future__ import annotations

from functools import lru_cache

from app.core.config import get_settings
from app.integrations.payments.fake import SimulatedPaymentsClient
from app.integrations.payments.interface import PaymentsClient


@lru_cache(maxsize=1)
def get_payments_client() -> PaymentsClient:
    settings = get_settings()
    if settings.payment_provider == "simulated":
        return SimulatedPaymentsClient()
    if settings.payment_provider in ("flutterwave", "pesapal"):
        raise NotImplementedError(
            f"{settings.payment_provider} adapter is implemented in M6 (see ADR-003)"
        )
    raise ValueError(f"Unknown PAYMENT_PROVIDER: {settings.payment_provider}")


def reset_payments_client() -> None:
    get_payments_client.cache_clear()
