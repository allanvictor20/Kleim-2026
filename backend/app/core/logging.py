"""Structured logging and PII masking (M0).

Logs are one JSON object per line so staging and production can be searched by
`request_id`. Customer phone numbers and addresses must never appear in a log
line (CONTRIBUTING.md section 9) -- use `mask_phone` and `mask_address`.
"""
from __future__ import annotations

import json
import logging
import sys
from typing import Any

from app.core.config import Settings
from app.core.context import get_request_id

_RESERVED = frozenset(
    {
        "args", "asctime", "created", "exc_info", "exc_text", "filename", "funcName",
        "levelname", "levelno", "lineno", "module", "msecs", "message", "msg", "name",
        "pathname", "process", "processName", "relativeCreated", "stack_info",
        "taskName", "thread", "threadName",
    }
)


class JsonFormatter(logging.Formatter):
    """Render a record as a single JSON line, including the request id."""

    def format(self, record: logging.LogRecord) -> str:
        payload: dict[str, Any] = {
            "timestamp": self.formatTime(record, "%Y-%m-%dT%H:%M:%S%z"),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "request_id": get_request_id(),
        }
        for key, value in record.__dict__.items():
            if key not in _RESERVED and not key.startswith("_"):
                payload[key] = value
        if record.exc_info:
            payload["exception"] = self.formatException(record.exc_info)
        return json.dumps(payload, default=str)


def configure_logging(settings: Settings) -> None:
    """Install the JSON formatter on the root logger, once."""
    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(JsonFormatter())
    root = logging.getLogger()
    root.handlers = [handler]
    root.setLevel(logging.DEBUG if settings.is_development else logging.INFO)
    # uvicorn installs its own handlers; route them through ours instead.
    for name in ("uvicorn", "uvicorn.error", "uvicorn.access"):
        uvicorn_logger = logging.getLogger(name)
        uvicorn_logger.handlers = []
        uvicorn_logger.propagate = True


def init_sentry(settings: Settings) -> None:
    """Enable Sentry only when a DSN is configured."""
    if not settings.sentry_dsn:
        return
    try:
        import sentry_sdk
    except ImportError:  # pragma: no cover - optional in local installs
        logging.getLogger(__name__).warning("SENTRY_DSN is set but sentry-sdk is not installed")
        return
    sentry_sdk.init(dsn=settings.sentry_dsn, environment=settings.app_env, send_default_pii=False)


def mask_phone(phone: str | None) -> str:
    """`+256700000001` -> `+2567****0001`. Safe to log."""
    if not phone:
        return "-"
    digits = phone.strip()
    if len(digits) <= 8:
        return "*" * len(digits)
    return f"{digits[:5]}{'*' * (len(digits) - 9)}{digits[-4:]}"


def mask_address(address: str | None) -> str:
    """Keep only the coarse area so a log line cannot locate a customer."""
    if not address:
        return "-"
    head, _, _ = address.partition(",")
    head = head.strip()
    return f"{head[:12]}..." if len(head) > 12 else head
