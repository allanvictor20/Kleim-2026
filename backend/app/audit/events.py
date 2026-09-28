"""Audit event subscribers (M0).

Empty by design: M0 has no domain events yet. From M5 the state machine
publishes `order.*` and `delivery.*`, and the admin module (M10) subscribes here
so privileged changes are audited without each module remembering to call
`record_audit` twice.
"""
from __future__ import annotations
