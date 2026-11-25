# Phase 2: automated + cloud

**Goal:** the pipeline runs itself, and the dashboard is public.

**Estimate:** about 5 weeks, part time.

## Scope

| Week | Deliverable | Acceptance criteria |
|---|---|---|
| 6 | Live sync | Hourly recently-played pull into `raw.plays_api`. Re-runs insert nothing new. `stg_plays` unions export and API; the export wins where they overlap. |
| 7 | Cloud | S3 raw zone created with Terraform. Warehouse on MotherDuck. |
| 8 | Enrichment | Track metadata (including ISRC), MusicBrainz genres, hourly weather. `dim_artist` as a dbt snapshot. |
| 9 | Orchestration | GitHub Actions schedules (hourly sync, nightly build), then Dagster with retries, backfills and failure alerts. |
| 10 | Ship | Public dashboard, data health page, yearly totals reconciled against stats.fm with differences explained. |

## Done when

Yesterday's plays appear on the public dashboard with no manual steps.

## Before starting

Request a fresh export so it covers everything up to the day the sync starts. See [the runbook](../runbooks/request-spotify-export.md).

## Out of scope

Photos, location, the front end and other users (phases 3 to 5).
