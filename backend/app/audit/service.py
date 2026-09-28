"""Audit trail (AUD-01, M0).

Every privileged, financial or configuration change writes one row here. The
helper is intentionally the only way in, so the shape of an audit entry is
identical across modules.
"""
from __future__ import annotations

import logging
import uuid
from typing import Any, Protocol

from sqlalchemy.orm import Session

from app.audit import repository
from app.audit.models import AuditLog

logger = logging.getLogger(__name__)

# Keys whose values must never be copied into before/after snapshots
# (CONTRIBUTING.md section 9).
_REDACTED_KEYS = frozenset(
    {
        "phone", "contact_phone", "password", "code", "code_hash", "otp",
        "token", "access_token", "refresh_token", "token_hash", "secret",
        "api_key", "payout_number", "landmark", "notes",
    }
)
_REDACTED = "[redacted]"


class Actor(Protocol):
    """Anything with an id can act; M1's User satisfies this."""

    id: uuid.UUID


class Target(Protocol):
    id: uuid.UUID


def redact(values: dict[str, Any] | None) -> dict[str, Any] | None:
    """Drop personal data from a snapshot before it is stored."""
    if values is None:
        return None
    return {
        key: (_REDACTED if key in _REDACTED_KEYS else value) for key, value in values.items()
    }


def record_audit(
    session: Session,
    actor: Actor | uuid.UUID | None,
    action: str,
    target: Target | tuple[str, uuid.UUID],
    before: dict[str, Any] | None = None,
    after: dict[str, Any] | None = None,
) -> AuditLog:
    """Append one audit entry.

    `actor` is the acting user, or None for a system action such as an order
    expiring. `action` is a dotted verb from the SDD, e.g. `seller.approve`.
    `target` is either a model instance (its class name becomes `target_type`)
    or an explicit `(target_type, id)` pair.
    """
    if isinstance(target, tuple):
        target_type, target_id = target
    else:
        target_type, target_id = type(target).__name__.lower(), target.id

    actor_id = actor if isinstance(actor, uuid.UUID) or actor is None else actor.id

    entry = repository.insert(
        session,
        actor_user_id=actor_id,
        action=action,
        target_type=target_type,
        target_id=target_id,
        before=redact(before),
        after=redact(after),
    )
    logger.info(
        "audit recorded",
        extra={"action": action, "target_type": target_type, "target_id": str(target_id)},
    )
    return entry
