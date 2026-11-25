# Phase 1: local MVP

**Goal:** build the whole pipeline on my laptop from the Spotify export alone, and answer "what was I listening to in June 2022?"

**Estimate:** about 5 weeks, part time.

## Scope

| Week | Deliverable | Acceptance criteria |
|---|---|---|
| 1 | Skeleton | Repo, Makefile, DuckDB, dbt project, CI passing on a fake export. *(Scaffolded.)* |
| 2 | Backfill | `make load` builds `raw.plays_export` from the real export. Re-running gives identical row counts. `ip_addr` is never stored. Data profiled: date range, podcast share, nulls. |
| 3 | Staging | `stg_plays` with UTC and NZ time and a 30-second stream flag. Tests on keys, nulls and accepted values. |
| 4 | Marts | `int_sessions`, `fct_plays`, `fct_sessions`, `dim_date`, `mart_monthly_top`, each with its grain documented and tested. |
| 5 | Dashboard | Evidence running locally with time machine, eras and habits pages. README updated. |

## Done when

From a fresh clone, `make setup && make all` builds every model from the export, and the dashboard shows what I played in June 2022.

## Out of scope

- The Spotify API and the hourly sync (phase 2).
- Any cloud service: S3, MotherDuck, deployment (phase 2).
- Orchestration beyond `make` (phase 2).
- Track metadata, genres, weather (phase 2).
- Podcasts and audiobooks.

## Open questions

- What does the export's earliest `ts` look like? That decides the start of `dim_date`.
- Are there exact duplicate plays (same `ts` and track) in the export? Check during profiling and decide how `stg_plays` handles them.
