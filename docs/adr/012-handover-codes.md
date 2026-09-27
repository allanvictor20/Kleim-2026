# ADR-012: Pickup, drop-off and return confirmation codes

- **Status:** Accepted
- **Date:** [project start]
- **Related:** SDD §12.2, §21, RID-03; Implementation Plan M7

## Context

Disputes about whether items were collected, delivered or returned are common in delivery businesses, and cash is involved.

## Decision

Each delivery has three 4-digit single-use codes: the seller gives the pickup code to the rider, the customer gives the drop-off code to the rider, and the store confirms returns with a return code. Codes are stored hashed and lock after 5 wrong attempts.

## Consequences

- Positive: proof of each handover; fewer disputes; supports COD reconciliation.
- Negative: an extra step at each handover; lost codes need a support path.
- Follow-up: ops can reissue a code after verifying identity by phone; every reissue is audited.
