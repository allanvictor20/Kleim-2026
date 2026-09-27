# core (M0)

Shared platform code: settings, database session, Redis, error classes (SDD §15.1 shape), request-ID middleware, logging, domain event bus, idempotency middleware, generic state-machine helper, clock.

See Implementation Plan §4 (M0) for deliverables, business rules, tests and exit criteria.

| File | Holds |
| --- | --- |
| `config.py` | `Settings` read from the environment; `get_settings()` |
| `clock.py` | `now()` in UTC, and `frozen()` so tests control time |
| `db.py` | Engine, session dependency, `Base` with the Alembic naming convention |
| `redis.py` | Async Redis client and health check |
| `errors.py` | `AppError` and subclasses; the handlers that emit the SDD §15.1 envelope |
| `context.py` | Request-id context variable |
| `middleware.py` | `RequestIdMiddleware` |
| `logging.py` | JSON formatter, Sentry hook, `mask_phone()` / `mask_address()` |
| `events.py` | In-process domain event bus |
| `idempotency.py` | `Idempotency-Key` replay for 24 h (NFR-11) |
| `state_machine.py` | Generic transition validator, reused by orders (M5) and deliveries (M7) |
| `security.py` | Argon2 hashing, JWT helpers, OTP and public-code generation |
| `settings_store.py` | `fee_configs` reader and integer rate arithmetic (ADM-04) |

Two rules this package exists to enforce: nothing outside it builds an error
body, and nothing outside it assigns a `status` attribute directly.
