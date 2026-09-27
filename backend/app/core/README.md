# core (M0)

Shared platform code: settings, database session, Redis, error classes (SDD §15.1 shape), request-ID middleware, logging, domain event bus, idempotency middleware, generic state-machine helper, clock.

See Implementation Plan §4 (M0) for deliverables, business rules, tests and exit criteria.

Expected files:

- `config.py`
- `db.py`
- `errors.py`
- `events.py`
- `idempotency.py`
- `state_machine.py`
- `clock.py`
- `logging.py`
- `security.py`
