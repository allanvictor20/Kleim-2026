# ADR-007: Double-entry ledger for all money movements

- **Status:** Accepted
- **Date:** [project start]
- **Related:** SDD §4.3, NFR-12; Implementation Plan M9

## Context

Money moves between customers, sellers, riders, the platform and the payment provider, including cash held by riders and partial returns. Storing balances as editable numbers makes errors impossible to trace.

## Decision

Every financial effect is posted as a balanced set of ledger entries (sum = 0) against accounts. Balances are always derived by summing entries. Entries are append-only; corrections are reversing entries.

## Consequences

- Positive: any figure shown to a seller or rider can be traced; reconciliation is a query.
- Negative: more design effort; developers must learn posting rules.
- Follow-up: nightly imbalance check; reconciliation test on 50 seeded orders.

## Alternatives considered

| Option | Why not chosen |
| --- | --- |
| Balance columns on sellers and riders | Untraceable errors; race conditions on updates |
| Accounting software export only | Does not give sellers and riders live balances |
