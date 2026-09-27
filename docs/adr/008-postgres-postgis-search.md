# ADR-008: PostgreSQL with PostGIS and pg_trgm for geo and search

- **Status:** Accepted
- **Date:** [project start]
- **Related:** SDD §9; Database Design §1.2; Implementation Plan M3

## Context

Discovery needs distance from the customer, delivery zones and typo-tolerant text search. The catalogue at pilot scale is a few thousand products.

## Decision

Use PostGIS for points, polygons and distance, Postgres full-text search for relevance and pg_trgm for typos. No separate search engine in the MVP; move to Meilisearch or Typesense only if search latency or relevance fails NFR-01.

## Consequences

- Positive: one database, transactional consistency between stock and search, fewer moving parts.
- Negative: relevance tuning is more manual than in a dedicated engine.
- Follow-up: performance test on 5,000 products in M3.

## Alternatives considered

| Option | Why not chosen |
| --- | --- |
| Elasticsearch | Heavy to run; unnecessary at this scale |
| Meilisearch from day one | Extra sync logic between stock and index |
