# ADR-005: One store per cart and per order in the MVP

- **Status:** Accepted
- **Date:** [project start]
- **Related:** SDD §2.1, CUS-04, §30; Implementation Plan M4

## Context

A cart with items from several boutiques would need split orders, several pickups, several riders or route batching, split payments and partial failures. That complexity would not fit the semester.

## Decision

A cart belongs to one store. Adding an item from another store returns `CART_STORE_CONFLICT`, and the app offers to start a new bag. One order equals one pickup and one delivery.

## Consequences

- Positive: simple order, delivery and payment models; one delivery fee per order.
- Negative: customers wanting an outfit from two shops must place two orders.
- Follow-up: track how often the conflict appears; if frequent during the pilot, design multi-store baskets (SDD §29).

## Alternatives considered

| Option | Why not chosen |
| --- | --- |
| Multi-store cart split into several orders | Doubles delivery and payment complexity for the MVP |
