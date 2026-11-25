# Backtrack

An ELT pipeline over my lifetime Spotify listening history: raw export files → a tested star schema in DuckDB → a dashboard that answers "what was I listening to in June 2022?"

**Why:** I wanted to see exactly what I was playing in any month, years back. Spotify's API only remembers my last 50 plays, and no existing tool gave me that view over data I control. So I'm building it, and using it to learn data engineering properly.

> Status: **Phase 1 (local MVP)** in progress. See the [roadmap](#roadmap).

## Architecture

```mermaid
flowchart LR
    subgraph SRC["Sources"]
        EXP["Spotify export<br/>lifetime JSON"]
        API["Spotify Web API<br/>last 50 plays"]:::p2
        ENR["MusicBrainz + Open-Meteo<br/>genres, weather"]:::p2
    end

    subgraph EL["Extract & load (Python)"]
        LOAD["load_export.py<br/>full refresh"]
        SYNC["sync_recently_played.py<br/>hourly, cursor"]:::p2
        ENRJ["enrich.py<br/>metadata, genres, weather"]:::p2
    end

    RAW[("Raw zone<br/>local folder → S3")]

    subgraph WH["Warehouse: DuckDB → MotherDuck"]
        R["raw<br/>plays_export, plays_api,<br/>tracks, artists, weather"]
        S["staging<br/>stg_plays"]
        M["marts<br/>fct_plays, fct_sessions,<br/>dim_track, dim_artist, dim_date"]
        R -->|dbt| S -->|dbt| M
    end

    DASH["Evidence dashboard<br/>local → public site"]

    EXP --> LOAD
    API --> SYNC
    ENR --> ENRJ
    LOAD --> RAW
    SYNC --> RAW
    ENRJ --> RAW
    RAW --> R
    M --> DASH

    ORCH["Orchestration runs every step:<br/>make (P1) → GitHub Actions → Dagster (P2)"]:::ops

    classDef p2 stroke-dasharray: 5 5
    classDef ops fill:#eee,stroke:#999
```

Dashed boxes arrive in phase 2. More detail in [docs/architecture.md](docs/architecture.md).

**Stack:** Python, DuckDB, Parquet, dbt, Evidence. Phase 2 adds MotherDuck, S3, Terraform, GitHub Actions and Dagster.

**No app database:** plays are append-only history that's only analysed, so they go straight into the warehouse. See [ADR 0001](docs/adr/0001-no-app-database.md).

## Run it

Needs Python 3.11+ and `make`.

```bash
make setup      # virtualenv + dependencies
make fake       # no export yet? generate a fake one in data/export/
make all        # load the export, then build and test every dbt model
make docs       # browse lineage and table docs in your browser
```

To use your real data, put the `Streaming_History_Audio_*.json` files from your Spotify export in `data/export/` and run `make all`. `data/` is gitignored and nothing personal is committed. How to get the export: [docs/runbooks/request-spotify-export.md](docs/runbooks/request-spotify-export.md).

## Roadmap

| Phase | Scope | Done when |
|---|---|---|
| 1. Local MVP | Export → DuckDB → dbt → local dashboard | `make all` on a fresh clone builds everything and shows June 2022 |
| 2. Automated + cloud | Hourly API sync, S3, MotherDuck, orchestration, public dashboard | Yesterday's plays appear on the public dashboard with no manual steps |
| 3. Photos | Photo metadata joined to plays | Any day shows plays and photos in order |
| 4. Google Timeline | Places and trips joined to plays and photos | The day view shows where I was, what I played and my photos |
| 5. Front end + other people | Timeline UI, accounts, more music services | Someone else can upload their exports and see only their own timeline |

Phase specs live in [docs/phases/](docs/phases/).

## Key decisions

Recorded as ADRs in [docs/adr/](docs/adr/):

- [0001](docs/adr/0001-no-app-database.md): no app database. Plays go straight to the warehouse.
- [0002](docs/adr/0002-duckdb-as-warehouse.md): DuckDB locally, MotherDuck in phase 2.
- [0003](docs/adr/0003-full-refresh-export-loader.md): the export loader does a full refresh, not incremental.

## Repo layout

```
ingestion/     Python loaders and the fake data generator
transform/     dbt project
dashboard/     Evidence site
docs/          architecture, data model, data sources, phases, ADRs, runbooks, retros
tests/         pytest
```

## Privacy

This project processes personal data. Real listening data never leaves my machine or private storage. The export's IP address field is dropped at load time. Tests, CI and any public demo use generated fake data.
