# 0001: No app database

- **Status:** accepted
- **Date:** 2026-11-25

## Context

The first design had an app with ratings, mood tags and a rediscover queue, backed by Postgres (OLTP), with data copied from there into a warehouse (OLAP). I decided I don't want those app features. What's left is listening history: append-only events that are only ever analysed.

## Decision

Load plays straight into the warehouse. No Postgres in phases 1 to 4.

## Alternatives considered

- **Postgres first, then copy to the warehouse:** an extra hop with no purpose. Nothing writes to it except the loader, and nothing reads single rows from it.
- **Warehouse as the app backend later:** rejected for when an app exists. DuckDB has a single writer, and warehouses are slow and costly for row-level reads and writes.

## Consequences

- Simpler stack and faster progress on the core data engineering work.
- Phase 5 (front end, accounts, notes) will need Postgres for app data. When that happens, events still go straight to the warehouse and app data is replicated in, which is the same pattern companies use for product events versus app databases.
