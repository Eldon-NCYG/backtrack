# CLAUDE.md

Guidance for Claude (and other coding agents) working in this repository.

## This is a learning project

I'm building this to learn data engineering properly and to have a portfolio project I can explain in interviews. Shipping fast matters less than understanding every piece.

**About me:** I have software experience (Python, SQL, git, APIs, CRMs and GTM data pipelines). I'm newer to the data engineering stack used here: DuckDB, dbt, dimensional modelling, orchestration (Dagster), Terraform and cloud storage. Pitch explanations at that level. Don't explain what a function or a for loop is. Do explain what a dbt incremental model is the first time it comes up.

## How to work with me

**Explain every change.** After any change, finish with a short summary:

1. **What changed:** files touched and what each change does.
2. **Why:** the reasoning, and the alternative you didn't pick (one line is enough).
3. **Concepts:** any data engineering idea the change relies on, explained briefly the first time it appears. Link to the official docs when useful.
4. **How to check it:** the command to run and what I should see.

**Keep it proportionate.** A one-line fix gets a one-line explanation. A new model or pipeline step gets the full summary. Be direct and skip filler.

**Work in small steps.** Prefer one coherent change at a time over a large drop of code. If a task needs more than a few files, outline the plan first and wait for my go-ahead.

**Let me drive sometimes.** When a task is a good learning exercise (a first dbt model, a window function, a test), offer to let me write it and review it, rather than writing it outright.

**Flag decisions.** When there's a real choice between approaches, lay out the options with trade-offs and a recommendation. If it's a decision worth defending in an interview, suggest an ADR in `docs/adr/` and offer to draft it.

**Ask before:** adding a dependency, changing the project structure, touching CI, or doing anything that costs money or touches cloud resources.

## Project context

Read these before making changes:

- `README.md`: what the project is and how to run it.
- `docs/phases/`: the spec for each phase. **Current phase: 1 (local MVP).** Don't build phase 2+ features unless I ask.
- `docs/architecture.md`: how the pieces fit.
- `docs/data-model.md`: tables, grains and naming.
- `docs/data-sources.md`: the Spotify export and API formats.
- `docs/adr/`: decisions already made. Don't contradict one without saying so.

## Conventions

- **Timestamps:** store in UTC. Convert to `Pacific/Auckland` in dbt staging only.
- **`user_id` on every table**, even though there is one user today. Default is `1`.
- **Provider-neutral names:** `stg_plays` with a `source` column, not `stg_spotify_plays`. Provider IDs (Spotify URI, ISRC) are columns, not table names.
- **Loader contract:** every loader in `ingestion/` takes raw files in, writes one raw table out, is safe to re-run, and prints row count and date range.
- **dbt layers:** `staging` (rename, cast, filter; no joins), `intermediate` (reusable logic), `marts` (facts and dimensions the dashboard reads). Document the grain of every mart in its `.yml`.
- **Tests:** every primary key gets `unique` and `not_null` in dbt. Python logic gets pytest.
- **SQL style:** lowercase keywords, CTEs over subqueries, one column per line in selects.
- **Docs move with code:** if a change affects behaviour, update the relevant doc in the same change.

## Privacy rules

- Never commit anything under `data/`, any `*.duckdb` file, or `.env`.
- Never print, log or paste rows of my real listening data into docs, tests or commit messages. Use the fake data generator (`ingestion/fake_export.py`) for examples and tests.
- The export's `ip_addr` field must be dropped at load time and never stored.

## Commands

```bash
make setup     # create the virtualenv, install Python deps and dbt packages
make fake      # generate a fake export in data/export/ for local development
make load      # load the export into the warehouse (safe to re-run)
make build     # dbt build: run and test every model
make test      # pytest
make lint      # ruff
make all       # load + build
```

## Folder map

```
ingestion/     Python loaders (one per source) and the fake data generator
transform/     dbt project: staging, intermediate, marts, tests
dashboard/     Evidence site (phase 1, week 5)
docs/          architecture, data model, phase specs, ADRs, runbooks, retros
tests/         pytest
data/          gitignored: real export and local raw zone
```
