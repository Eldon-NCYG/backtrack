# Phase 2: backfill, automated + cloud

**Goal:** my whole listening history is in, the pipeline runs itself off my laptop, and the dashboard is public.

**Estimate:** about 5 weeks, part time.

## Scope

| Week | Deliverable | Acceptance criteria |
|---|---|---|
| 6 | Backfill | The export loader builds `raw.plays_export` from the real export. Re-running gives identical row counts. `ip_addr` is never stored. Data profiled: date range, podcast share, nulls. `stg_plays` unions export and API; the export wins where they overlap. The 30-second stream flag is added. Time machine and eras dashboard pages. |
| 7 | Cloud | S3 raw zone created with Terraform. Warehouse on MotherDuck. |
| 8 | Enrichment | Track metadata (including ISRC) for tracks that only appear in the export, MusicBrainz genres, hourly weather. `dim_artist` as a dbt snapshot. |
| 9 | Orchestration | The hourly sync moves from launchd on my laptop to GitHub Actions schedules (hourly sync, nightly build), then Dagster with retries, backfills and failure alerts. |
| 10 | Ship | Public dashboard, data health page, yearly totals reconciled against stats.fm with differences explained. |

## Done when

The dashboard shows what I played in June 2022, and yesterday's plays appear on the public dashboard with no manual steps.

## Before starting

Request the export a week or two before phase 1 ends, because it takes days to arrive. It must be requested after the hourly sync started, so the two overlap and the export fills any gaps the laptop sync left. See [the runbook](../runbooks/request-spotify-export.md).

## Out of scope

Photos, location, the front end and other users (phases 3 to 5).

## Open questions

- What does the export's earliest `ts` look like? That decides the start of `dim_date`.
- Are there exact duplicate plays (same `ts` and track) in the export? Check during profiling and decide how `stg_plays` handles them.
- Does API `played_at` mark the start or the end of a play? The union needs the answer to match plays across the two sources. See [data-sources.md](../data-sources.md).
- Spotify's development mode stopped returning artist `popularity` and `followers` in 2026. What does the `dim_artist` snapshot track without them?
- Development mode removed the batch endpoints (`GET /tracks?ids=`). Enrichment is one request per track, so it needs rate limiting and a cache.
