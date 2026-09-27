# ADR-001: Build a modular monolith, not microservices

- **Status:** Accepted
- **Date:** [project start]
- **Related:** SDD §8, §10, §30; Implementation Plan M0

## Context

The platform has many domains (catalogue, orders, payments, delivery, ledger), but the team is 4–5 part-time students with one semester. Orders, stock and payments must change together consistently. Operating many services would consume time the team does not have.

## Decision

Build one FastAPI application and one worker process from a single codebase, split into modules under `backend/app/<module>/`. Modules talk only through service functions and domain events, never through each other’s tables.

## Consequences

- Positive: one deployment, one database transaction for order + stock, simple local setup, easy debugging.
- Positive: clear module boundaries keep the option to extract a service later (for example notifications or tracking).
- Negative: one bad deployment affects everything; mitigated by CI, staging and quick rollback.
- Follow-up: an import-linter rule in CI blocks cross-module imports of `models.py` and `repository.py`.

## Alternatives considered

| Option | Why not chosen |
| --- | --- |
| Microservices per domain | Distributed transactions for stock and payment; heavy DevOps load; slower delivery |
| Unstructured monolith | Fast at first, but modules would tangle and block later extraction |
