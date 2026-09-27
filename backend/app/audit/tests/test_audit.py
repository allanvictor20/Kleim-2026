"""Audit trail (AUD-01): every privileged change leaves a row that cannot be
altered afterwards."""
from __future__ import annotations

import uuid

import pytest
from sqlalchemy import text
from sqlalchemy.exc import DatabaseError
from sqlalchemy.orm import Session

from app.audit import repository, service
from app.audit.models import AuditLog
from tests.markers import requires_database

pytestmark = requires_database


def test_record_audit_writes_a_row(session: Session) -> None:
    actor = uuid.uuid4()
    target = uuid.uuid4()

    entry = service.record_audit(
        session,
        actor,
        "seller.approve",
        ("store", target),
        before={"status": "pending"},
        after={"status": "active"},
    )

    assert entry.id is not None
    assert entry.actor_user_id == actor
    assert entry.action == "seller.approve"
    assert entry.target_type == "store"
    assert entry.target_id == target
    assert entry.before == {"status": "pending"}
    assert entry.after == {"status": "active"}
    assert entry.created_at is not None


def test_a_system_action_has_no_actor(session: Session) -> None:
    """An order expiring on a timer is nobody's action."""
    entry = service.record_audit(
        session, None, "order.expire", ("order", uuid.uuid4()), after={"status": "expired"}
    )

    assert entry.actor_user_id is None


def test_target_type_comes_from_the_model_when_an_instance_is_passed(session: Session) -> None:
    existing = service.record_audit(session, None, "audit.self", ("audit_logs", uuid.uuid4()))

    entry = service.record_audit(session, None, "test.action", existing)

    assert entry.target_type == "auditlog"
    assert entry.target_id == existing.id


def test_personal_data_is_redacted_from_snapshots(session: Session) -> None:
    """A snapshot must not become a back door for phone numbers
    (CONTRIBUTING.md section 9)."""
    entry = service.record_audit(
        session,
        None,
        "address.update",
        ("address", uuid.uuid4()),
        before={"phone": "+256700000001", "area": "Kamwokya", "landmark": "blue gate"},
        after={"phone": "+256700000002", "area": "Ntinda", "landmark": "the church"},
    )

    assert entry.before is not None and entry.after is not None
    assert entry.before["phone"] == "[redacted]"
    assert entry.before["landmark"] == "[redacted]"
    assert entry.before["area"] == "Kamwokya"
    assert "+256700000002" not in str(entry.after)


def test_entries_are_listed_newest_first_for_a_target(session: Session) -> None:
    target = uuid.uuid4()
    service.record_audit(session, None, "store.create", ("store", target))
    service.record_audit(session, None, "store.approve", ("store", target))
    service.record_audit(session, None, "store.suspend", ("other", uuid.uuid4()))

    entries = repository.list_for_target(session, "store", target)

    assert [entry.action for entry in entries] == ["store.approve", "store.create"]


def test_audit_logs_reject_an_update(session: Session) -> None:
    """Append-only (Database Design section 2.6), enforced by a trigger so it
    holds even for someone with a psql prompt."""
    entry = service.record_audit(session, None, "store.approve", ("store", uuid.uuid4()))
    session.flush()

    with pytest.raises(DatabaseError):
        session.execute(
            text("UPDATE audit_logs SET action = 'tampered' WHERE id = :id"), {"id": entry.id}
        )


def test_audit_logs_reject_a_delete(session: Session) -> None:
    entry = service.record_audit(session, None, "store.approve", ("store", uuid.uuid4()))
    session.flush()

    with pytest.raises(DatabaseError):
        session.execute(text("DELETE FROM audit_logs WHERE id = :id"), {"id": entry.id})


def test_the_table_matches_the_data_dictionary(session: Session) -> None:
    columns = {column.name for column in AuditLog.__table__.columns}
    assert columns == {
        "id",
        "actor_user_id",
        "action",
        "target_type",
        "target_id",
        "before",
        "after",
        "created_at",
    }
