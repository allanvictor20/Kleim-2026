<p align="center"><img src="docs/design/brand/kleim-logo-512.png" alt="Kleim logo" width="120"></p>

# Kleim

Kleim is a “Glovo-for-Fashion” marketplace for Kampala: customers discover outfits from nearby boutiques by occasion, size and budget, and receive them the same day by boda, with try-on at the door.

This repository holds the full platform: a FastAPI modular monolith, a background worker and four React apps (customer, seller, rider PWA, admin).

## Documentation

| Document | Where |
| --- | --- |
| Software Design Description v1.1 | `docs/sdd/01_Kleim_Software_Design_Description_v1.1.docx` |
| Implementation Plan (modules M0–M13) | `docs/sdd/02_Kleim_Implementation_Plan_v1.0.docx` |
| Database Design and ERD | `docs/sdd/03_Kleim_Database_Design_and_ERD.docx` |
| API contract (OpenAPI 3.1) | `docs/api/openapi.yaml`; live at http://localhost:8000/docs |
| UI/UX Style Guide and prototype | `docs/design/` |
| Architecture Decision Records | `docs/adr/` |
| Operations Runbook | `docs/ops/runbook.md` |
| How we work | `CONTRIBUTING.md` |

## Tech stack

Python 3.12, FastAPI, SQLAlchemy 2, Pydantic v2, Alembic, PostgreSQL 16 + PostGIS, Redis, ARQ · React, TypeScript, Vite, TanStack Query, Tailwind, Plus Jakarta Sans · Docker, GitHub Actions · Cloudinary, Africa’s Talking, Firebase Cloud Messaging.

## Repository layout

```
backend/
  app/
    core/            config, db, errors, events, idempotency, state machine
    identity/ profiles/ addresses/ stores/ catalog/ search/
    cart/ pricing/ orders/ payments/ ledger/ payouts/
    delivery/ tracking/ recommendations/ notifications/
    support/ admin/ audit/
    integrations/    sms, maps, payments, push (real + fake adapters)
    workers/         ARQ tasks and schedules
  alembic/
  tests/
frontend/
  apps/customer  apps/seller  apps/rider  apps/admin
  packages/ui  packages/api-client  packages/types
infra/           Dockerfiles, deployment config
.github/         CI workflows, issue and pull request templates
docs/            sdd/, api/, design/, adr/, ops/ (see docs/README.md)
docker-compose.yml
```

## Quick start (about 15 minutes)

Prerequisites: Docker Desktop (or Docker Engine + Compose), Node.js 20+, pnpm 9+, Git. Python is only needed if you run the backend outside Docker.

```
git clone https://github.com/<org>/kleim.git
cd kleim
cp .env.example .env                 # defaults work for local development
docker compose up -d                 # api, worker, db, redis, mailpit
docker compose exec api alembic upgrade head
docker compose exec api python -m app.scripts.seed   # 5 stores, 20 products, test users
cd frontend && pnpm install && pnpm dev   # starts all four frontend apps (after M0 scaffolds them)
```

| Service | URL |
| --- | --- |
| API and interactive docs | http://localhost:8000/docs |
| Customer app | http://localhost:5173 |
| Seller app | http://localhost:5174 |
| Rider PWA | http://localhost:5175 |
| Admin console | http://localhost:5176 |
| Mail and SMS catcher (dev) | http://localhost:8025 |

In development, OTP codes are not sent by SMS. They appear in the API logs (`docker compose logs -f api`) and in the dev catcher.

### Seed accounts

| Role | Phone | Notes |
| --- | --- | --- |
| Customer | +256700000001 | Has two saved addresses |
| Seller | +256700000002 | Owns Bella Boutique (approved) |
| Rider | +256700000003 | Approved, starts offline |
| Admin | +256700000009 | Full admin role |

## Everyday commands

| Task | Command |
| --- | --- |
| Backend tests | `docker compose exec api pytest` |
| Backend lint and types | `docker compose exec api ruff check . && docker compose exec api mypy app` |
| New migration | `docker compose exec api alembic revision --autogenerate -m "m5 add orders"` |
| Frontend tests | `cd frontend && pnpm test` |
| Frontend lint | `cd frontend && pnpm lint` |
| Regenerate API client | `pnpm --filter api-client generate` |
| End-to-end tests | `cd frontend && pnpm e2e` |
| Simulate a payment outcome (dev) | `POST /api/v1/dev/payments/{id}/simulate` or the Dev Payments page in the admin app |

## Environment variables

See `.env.example` for the full list. The most important:

| Variable | Purpose | Development default |
| --- | --- | --- |
| DATABASE_URL | PostgreSQL connection | postgres://app:app@db:5432/app |
| REDIS_URL | Redis connection | redis://redis:6379/0 |
| JWT_SECRET | Token signing key | dev-only value; set a long random value elsewhere |
| SMS_PROVIDER | `console` or `africastalking` | console |
| PAYMENT_PROVIDER | `simulated` or aggregator name | simulated |
| MAPS_PROVIDER | `osm` or `google` | osm |
| CLOUDINARY_URL | Image uploads | empty (uploads stored locally in dev) |
| SENTRY_DSN | Error reporting | empty |

Never commit a real `.env`. CI fails if one is found.

## Environments

| Environment | Deploys | Data |
| --- | --- | --- |
| Local | `docker compose up` | Seed data |
| Staging | Automatically on merge to `main` | Seed + performance data |
| Production | Manual promotion of a tagged release | Real data, daily backups |

## Project status

Current milestone: **[A / B / C]** — see the Implementation Plan for module status.

## Team

| Role | Name |
| --- | --- |
| Team lead | [name] |
| Backend lead | [name] |
| Backend | [name] |
| Frontend (customer) | [name] |
| Frontend (seller, rider, admin) | [name] |
| Supervisor | [name] |

## Licence

[To be decided — private for now.]
