# Phase 1: local MVP

**Goal:** build the whole pipeline on my laptop from the Spotify Web API alone, collecting plays from the first sync onward, and answer "what have I been listening to this week?"

**Estimate:** about 5 weeks, part time.

The API can't see anything older than the last 50 plays, so history from before the first sync waits for the export in [phase 2](phase-2-automated-cloud.md). Why the API goes first: [ADR 0004](../adr/0004-api-first-mvp.md).

## Scope

| Week | Deliverable | Acceptance criteria |
|---|---|---|
| 1 | Skeleton and access | Repo, Makefile, DuckDB, dbt project, CI passing on fake API responses. Fake data has its own raw zone and warehouse, so it can never mix with real plays. Spotify developer app created and a refresh token in `.env` ([runbook](../runbooks/spotify-api-setup.md)). |
| 2 | Sync | `make sync` pulls recently played into the raw zone, and `make load` builds `raw.plays_api` from it. Re-running either adds nothing new. Each sync records how many new plays it found. launchd runs `make sync all` hourly: sync, then load and build, so the dashboard stays current. A transient API error is retried within the run, and a run that still fails exits non-zero and leaves the cursor where it was. Credentials are never printed. |
| 3 | Staging | `stg_plays` with UTC and NZ time. Tests on keys, nulls and accepted values. |
| 4 | Marts | `int_sessions`, `fct_plays`, `fct_sessions`, `dim_date`, `mart_monthly_top`, each with its grain documented and tested. |
| 5 | Dashboard | Evidence running locally with recent plays, habits and data health pages. README updated. |

## Done when

From a fresh clone, `make setup && make fake && make all` builds every model from fake API data. On my laptop the hourly sync has run for a week without me touching it, and the dashboard shows what I played yesterday.

## Known limits

- **Gaps.** The API only holds the last 50 plays. If more than 50 tracks play between two syncs, the oldest are gone. The laptop sync misses hours when the laptop is off, so this will happen sometimes. The launchd job is scheduled with `StartCalendarInterval`, which runs a missed job once when the laptop wakes (`StartInterval` would skip it). That covers ordinary sleep. Any sync after the first that finds 50 new plays is flagged as a possible gap and shown on the data health page. The phase 2 export fills these gaps.
- **Failures and retries.** The next hourly run is the main retry. A failed sync lands nothing and leaves the cursor where it was, so the next run asks for the same window again. Within a run, transient errors (no network, a 429 rate limit, a 5xx) are retried up to three times with a growing wait, honouring `Retry-After` on a 429. This matters most on wake, when launchd can fire the job before the wifi is back. Auth errors are not retried: `invalid_grant` fails straight away and needs re-authorising by hand ([runbook](../runbooks/spotify-api-setup.md)). A run that still fails exits non-zero and logs the reason, without credentials. Nothing alerts me in phase 1: a failing sync shows up in the log and, if it lasts long enough, as a gap flag.
- **One writer.** DuckDB allows one writer at a time ([ADR 0002](../adr/0002-duckdb-as-warehouse.md)). The hourly job loads and builds after it syncs, so it can collide with a `make build` I run by hand. The sync step only writes files to the raw zone, so a collision never loses plays: the load fails cleanly and catches up on the next run.
- **Credentials expire.** The refresh token lasts 6 months and the developer app needs Spotify Premium. See the [runbook](../runbooks/spotify-api-setup.md).

## Out of scope

- The export, and any history from before the first sync (phase 2).
- `ms_played`, skips and the 30-second stream flag. The API doesn't return them (phase 2, from the export).
- Any cloud service: S3, MotherDuck, deployment (phase 2).
- Orchestration beyond `make` and one launchd job (phase 2).
- Genres, weather, and track metadata beyond what the API returns with each play (phase 2).
- Podcasts and audiobooks. The endpoint doesn't return them.

## Open questions

- Where does the sync cursor live: stored state, or derived from the latest `played_at` already loaded? Decide in week 2 and record it in an ADR, along with the key that makes re-runs safe. Either way, a failed run must not move it.
- Can the same track have two plays with the same `played_at`? Check on real data before choosing the key for `raw.plays_api`.
- Does `played_at` mark the start or the end of a play? It shifts session boundaries slightly. See [data-sources.md](../data-sources.md).
