# audit (M0)

audit_logs table and record_audit() helper (AUD-01).

See Implementation Plan §4 (M0) for deliverables, business rules, tests and exit criteria.

| File | Holds |
| --- | --- |
| `models.py` | `audit_logs`, per the Database Design data dictionary §4 |
| `repository.py` | Inserts and reads. No update or delete: the table is append-only |
| `service.py` | `record_audit(session, actor, action, target, before, after)` |
| `schemas.py` | `AuditEntry` for the admin read endpoints (M10) |
| `events.py` | Subscribers, added from M5 when domain events exist |
| `tests/` | Including the append-only trigger |

Append-only is enforced by a database trigger (Database Design §2.6), so it holds
even from a `psql` prompt. Snapshots passed to `record_audit` are redacted before
they are stored — an audit entry must not become a back door for phone numbers.

`actor_user_id` carries no foreign key until M1 creates `users`.

No `router.py` in M0: the admin-facing audit endpoints belong to M10.
