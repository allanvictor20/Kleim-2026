"""audit_logs queries (M0).

Deliberately offers no update or delete: the table is append-only.
"""
from __future__ import annotations

import uuid
from collections.abc import Sequence
from typing import Any

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.audit.models import AuditLog


def insert(
    session: Session,
    *,
    actor_user_id: uuid.UUID | None,
    action: str,
    target_type: str,
    target_id: uuid.UUID,
    before: dict[str, Any] | None,
    after: dict[str, Any] | None,
) -> AuditLog:
    entry = AuditLog(
        actor_user_id=actor_user_id,
        action=action,
        target_type=target_type,
        target_id=target_id,
        before=before,
        after=after,
    )
    session.add(entry)
    session.flush()
    return entry


def list_for_target(
    session: Session, target_type: str, target_id: uuid.UUID, limit: int = 50
) -> Sequence[AuditLog]:
    statement = (
        select(AuditLog)
        .where(AuditLog.target_type == target_type, AuditLog.target_id == target_id)
        .order_by(AuditLog.created_at.desc())
        .limit(limit)
    )
    return session.scalars(statement).all()


def list_by_actor(session: Session, actor_user_id: uuid.UUID, limit: int = 50) -> Sequence[AuditLog]:
    statement = (
        select(AuditLog)
        .where(AuditLog.actor_user_id == actor_user_id)
        .order_by(AuditLog.created_at.desc())
        .limit(limit)
    )
    return session.scalars(statement).all()
