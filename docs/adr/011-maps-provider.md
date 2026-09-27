# ADR-011: Maps and geocoding provider

- **Status:** Proposed (decide by week 2)
- **Date:** [date]
- **Related:** SDD §14; Implementation Plan M1; Open Decision 6

## Context

Addresses are pin-first with landmarks. The app needs a map for pin drop, road distance for fees, and tiles for the tracking view. Cost matters.

## Decision

Proposed: OpenStreetMap tiles with Nominatim and OSRM (self-hosted or free tier) for development; evaluate Google Maps Platform for the pilot if pin accuracy or routing quality is poor. All calls go through the maps adapter and results are cached.

## Consequences

- Positive: no cost during development; swap provider without code changes outside the adapter.
- Negative: OSM coverage of informal areas can be thinner; public Nominatim has strict usage limits.
- Follow-up: compare pin accuracy for 20 known Kampala locations before accepting.
