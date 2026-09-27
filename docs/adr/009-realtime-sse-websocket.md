# ADR-009: Server-Sent Events for timelines, WebSocket for riders

- **Status:** Accepted
- **Date:** [project start]
- **Related:** SDD §8; TRK-01; Implementation Plan M7, M8

## Context

Customers and sellers need status updates pushed to them; riders need job offers and must send location updates.

## Decision

Customers and sellers subscribe to `GET /orders/{id}/events` using SSE (one-way, auto-reconnect with `Last-Event-ID`). Riders use one WebSocket (`/rider/ws`) for offers and location. Redis pub/sub fans out events across API instances.

## Consequences

- Positive: SSE works through most proxies and is simple for one-way updates; WebSocket fits the rider’s two-way needs.
- Negative: two mechanisms to maintain; long-lived connections need proxy timeout tuning.
- Follow-up: clients fall back to polling every 10 seconds if SSE fails.

## Alternatives considered

| Option | Why not chosen |
| --- | --- |
| Polling only | Wasteful on mobile data; slow updates |
| WebSocket for everyone | More complex for one-way customer updates |
| Firebase Realtime Database | Splits the source of truth away from Postgres |
