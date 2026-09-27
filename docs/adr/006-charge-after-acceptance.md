# ADR-006: Request mobile-money payment only after the seller accepts

- **Status:** Accepted
- **Date:** [project start]
- **Related:** SDD §13.1, PAY-03; Implementation Plan M6

## Context

Unlike cards, mobile money cannot place a hold on funds. If customers pay at checkout, every rejected or expired order needs a refund, which is slow and damages trust. Boutique stock is also often inaccurate.

## Decision

On checkout, stock is reserved and the order waits for the seller. Only after acceptance does the system send the payment prompt (AWAITING_PAYMENT, 10-minute window, up to 3 prompts). Cash-on-delivery orders skip this step.

## Consequences

- Positive: almost no refunds for stock problems; customers never pay for unavailable items.
- Negative: an extra wait between order and payment; a customer may not approve, wasting the seller’s acceptance.
- Follow-up: measure payment completion rate after acceptance during the pilot.

## Alternatives considered

| Option | Why not chosen |
| --- | --- |
| Pay at checkout, refund on rejection | Refund delays and fees; poor trust |
| Cash on delivery only | Excludes customers who prefer mobile money; more cash handling |
