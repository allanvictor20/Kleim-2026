"""ARQ worker settings (M0).

`docker-compose.yml` runs `arq app.workers.settings.WorkerSettings`, so this
module must import cleanly even with no jobs registered.

Jobs land here as their module needs them:
M5 expire_unanswered_orders, M6 reconcile_payments, M7 offer timeouts,
M8 notification delivery, M9 payout batches, M11 reliability and stock reminders.
"""
from __future__ import annotations

from typing import Any

from arq.connections import RedisSettings

from app.core.config import get_settings
from app.core.db import dispose_engine
from app.core.logging import configure_logging, init_sentry


async def startup(ctx: dict[str, Any]) -> None:
    settings = get_settings()
    configure_logging(settings)
    init_sentry(settings)


async def shutdown(ctx: dict[str, Any]) -> None:
    dispose_engine()


class WorkerSettings:
    """Discovered by the `arq` CLI, which reads these as plain attributes."""

    redis_settings = RedisSettings.from_dsn(get_settings().redis_url)
    functions: list[Any] = []
    cron_jobs: list[Any] = []
    on_startup = startup
    on_shutdown = shutdown
    # A job that fails is retried with backoff; a stuck order must not be lost.
    max_tries = 3
    job_timeout = 60
