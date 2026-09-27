# ADR-002: Store all money as integer Uganda shillings

- **Status:** Accepted
- **Date:** [project start]
- **Related:** SDD §4, §11.1; Database Design §2.3

## Context

UGX has no minor unit in everyday use. Floating-point money causes rounding errors, and the ledger must reconcile to the shilling.

## Decision

Every monetary column is `integer` UGX. The API sends and receives integers. Only the pricing service performs arithmetic, and percentages (commission, discounts) are rounded half up to the nearest shilling at a single, tested point.

## Consequences

- Positive: exact sums, simple ledger checks, no currency-library dependency.
- Negative: supporting another currency later needs a `currency` column and conversion rules (already present on `ledger_accounts`).
- Follow-up: lint rule forbids `float` in pricing and ledger modules.

## Alternatives considered

| Option | Why not chosen |
| --- | --- |
| `numeric(12,2)` | Implies cents that do not exist in UGX; more room for inconsistent rounding |
| Floats | Rounding errors; unacceptable for money |
