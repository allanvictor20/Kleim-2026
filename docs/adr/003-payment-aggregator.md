# ADR-003: First payment aggregator for mobile money

- **Status:** Proposed (decide by week 8)
- **Date:** [date]
- **Related:** SDD §13; Implementation Plan M6, M12; Open Decision 5

## Context

Customers pay by MTN Mobile Money and Airtel Money; cash on delivery remains available. The MVP uses a simulated provider behind the `PaymentProvider` adapter. A licensed aggregator is needed for the pilot, and approval can take weeks.

## Decision

Proposed: apply to Flutterwave in week 8 as the first aggregator, with Pesapal as fallback. The final choice is recorded here once sandbox access and fees are confirmed.

Evaluation criteria: collection and disbursement for both MTN and Airtel in Uganda; webhook reliability and signature scheme; fees per transaction; settlement time; sandbox quality; onboarding requirements for a student-led or newly registered business.

## Consequences

- Positive: a licensed aggregator avoids holding customer funds directly (SDD §28 regulatory risk).
- Negative: fees reduce margin; onboarding may require business registration.
- Follow-up: compare at least two providers in a table added to this ADR before acceptance.

## Alternatives considered

| Option | Status |
| --- | --- |
| Flutterwave | Proposed first choice |
| Pesapal | Fallback |
| Direct MTN MoMo and Airtel APIs | Later, once volumes justify separate integrations |
