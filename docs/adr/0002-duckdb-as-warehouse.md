# 0002: DuckDB as the warehouse, MotherDuck in phase 2

- **Status:** accepted
- **Date:** 2026-11-25

## Context

The data is small: roughly 100k to 200k plays over several years. I want a real columnar warehouse and dbt, at no cost, with fast local iteration.

## Decision

Use DuckDB locally (a single file in `data/`) in phase 1. Move to MotherDuck in phase 2 so scheduled jobs and the dashboard can share one warehouse.

## Alternatives considered

- **Databricks:** built for Spark and lakehouse work at much larger scale. A lot to learn alongside everything else, for no benefit at this size.
- **Snowflake or BigQuery:** common in job ads, but cost money or need cloud setup from day one. dbt makes switching later mostly a profile change.
- **Postgres:** row-oriented, so it doesn't teach warehouse habits.

## Consequences

- Zero cost and instant setup. Tests run against a real warehouse in CI.
- DuckDB allows one writer at a time, so loaders and dbt must not run at once. Orchestration has to respect that in phase 2.
