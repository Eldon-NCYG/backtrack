# Phase 1: local MVP

**Goal:** build the whole pipeline on my laptop from the Spotify Web API alone, collecting plays from the first sync onward, and answer "what have I been listening to this week?"

**Estimate:** about 5 weeks, part time.

The API can't see anything older than the last 50 plays, so history from before the first sync waits for the export in [phase 2](phase-2-automated-cloud.md). Why the API goes first: [ADR 0004](../adr/0004-api-first-mvp.md).

## Scope

| Week | Deliverable | Acceptance criteria |
|---|---|---|
| 1 | Skeleton and access | Repo, Makefile, DuckDB, dbt project, CI passing on fake API responses. Spotify developer app created and a refresh token in `.env` ([runbook](../runbooks/spotify-api-setup.md)). |
| 2 | Sync | `make sync` pulls recently played into the raw zone, and `make load` builds `raw.plays_api` from it. Re-running either adds nothing new. Each sync records how many new plays it found. launchd runs it hourly. Credentials are never printed. |
| 3 | Staging | `stg_plays` with UTC and NZ time. Tests on keys, nulls and accepted values. |
| 4 | Marts | `int_sessions`, `fct_plays`, `fct_sessions`, `dim_date`, `mart_monthly_top`, each with its grain documented and tested. |
| 5 | Dashboard | Evidence running locally with recent plays, habits and data health pages. README updated. |

## Done when

From a fresh clone, `make setup && make fake && make all` builds every model from fake API data. On my laptop the hourly sync has run for a week without me touching it, and the dashboard shows what I played yesterday.

## Known limits

- **Gaps.** The API only holds the last 50 plays. If more than 50 tracks play between two syncs, the oldest are gone. The laptop sync misses hours when the laptop is off, so this will happen sometimes. launchd runs a missed job once when the laptop wakes, which covers ordinary sleep. A sync that finds 50 new plays is flagged as a possible gap and shown on the data health page. The phase 2 export fills these gaps.
- **One writer.** DuckDB allows one writer at a time ([ADR 0002](../adr/0002-duckdb-as-warehouse.md)). An hourly job can now collide with a `make build` I run by hand. The sync must fail cleanly and catch up on the next run.
- **Credentials expire.** The refresh token lasts 6 months and the developer app needs Spotify Premium. See the [runbook](../runbooks/spotify-api-setup.md).

## Out of scope

- The export, and any history from before the first sync (phase 2).
- `ms_played`, skips and the 30-second stream flag. The API doesn't return them (phase 2, from the export).
- Any cloud service: S3, MotherDuck, deployment (phase 2).
- Orchestration beyond `make` and one launchd job (phase 2).
- Genres, weather, and track metadata beyond what the API returns with each play (phase 2).
- Podcasts and audiobooks. The endpoint doesn't return them.

## Open questions

- Where does the sync cursor live: stored state, or derived from the latest `played_at` already loaded? Decide in week 2 and record it in an ADR, along with the key that makes re-runs safe.
- Can the same track have two plays with the same `played_at`? Check on real data before choosing the key for `raw.plays_api`.
- Does `played_at` mark the start or the end of a play? It shifts session boundaries slightly. See [data-sources.md](../data-sources.md).
