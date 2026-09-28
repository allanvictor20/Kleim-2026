"""Application settings (M0).

Every value comes from the environment; the names match `.env.example` at the
repository root. Modules read settings through `get_settings()` and never from
`os.environ` directly, so tests can override a single object.
"""
from __future__ import annotations

from functools import lru_cache
from typing import Literal

from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

Environment = Literal["development", "test", "staging", "production"]
SmsProvider = Literal["console", "africastalking"]
PaymentProvider = Literal["simulated", "flutterwave", "pesapal"]
MapsProvider = Literal["osm", "google"]


class Settings(BaseSettings):
    """Runtime configuration.

    Business values such as fees, commission and timers live in the
    `fee_configs` table (ADM-04); the timer fields here are only the fallbacks
    used before a row exists.
    """

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
        case_sensitive=False,
    )

    app_env: Environment = "development"
    api_base_url: str = "http://localhost:8000"

    database_url: str = "postgresql+psycopg://app:app@db:5432/app"
    redis_url: str = "redis://redis:6379/0"

    jwt_secret: str = "change-me-dev-only"
    jwt_algorithm: str = "HS256"
    access_token_minutes: int = 15
    refresh_token_days: int = 30

    sms_provider: SmsProvider = "console"
    africastalking_username: str = ""
    africastalking_api_key: str = ""

    payment_provider: PaymentProvider = "simulated"
    payment_webhook_secret: str = ""

    maps_provider: MapsProvider = "osm"
    google_maps_api_key: str = ""

    cloudinary_url: str = ""
    fcm_credentials_json: str = ""
    sentry_dsn: str = ""

    seller_response_minutes: int = 10
    payment_window_minutes: int = 10
    rider_offer_seconds: int = 45

    idempotency_ttl_seconds: int = 60 * 60 * 24

    # Browsers enforce same-origin, and the four apps run on their own ports in
    # development (README: 5173 customer, 5174 seller, 5175 rider, 5176 admin),
    # so the API has to name them. An explicit list, never "*": the API answers
    # with credentials, and a wildcard plus credentials is both refused by
    # browsers and wrong.
    cors_origins: list[str] = [
        "http://localhost:5173",
        "http://localhost:5174",
        "http://localhost:5175",
        "http://localhost:5176",
        "http://127.0.0.1:5173",
        "http://127.0.0.1:5174",
        "http://127.0.0.1:5175",
        "http://127.0.0.1:5176",
    ]

    @field_validator("cors_origins", mode="before")
    @classmethod
    def _split_origins(cls, value: object) -> object:
        """Accept a comma-separated CORS_ORIGINS, which is how .env carries a list."""
        if isinstance(value, str):
            return [origin.strip() for origin in value.split(",") if origin.strip()]
        return value

    @property
    def is_production(self) -> bool:
        return self.app_env == "production"

    @property
    def is_development(self) -> bool:
        return self.app_env == "development"


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    """Return the process-wide settings, read from the environment once."""
    return Settings()
