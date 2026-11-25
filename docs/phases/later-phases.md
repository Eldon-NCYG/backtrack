# Phases 3 to 5: life timeline

Outline only. Each phase gets a full spec when it starts.

## Phase 3: photos

- **Sources:** Google Takeout (photos with JSON sidecar files holding taken time and GPS). Apple Photos metadata via `osxphotos`. Not the Google Photos API, which since 2025 only lets apps read photos they created.
- **Build:** photo adapters into `raw.photos` (metadata only), thumbnails in private storage, `stg_photos`, shared `dim_place`, photo events in `fct_life_events`, a "day view".
- **Done when:** any day shows plays and photos in order.

## Phase 4: Google Timeline

- **Sources:** the Timeline export from Google Maps on the phone, plus older Takeout history if available. One adapter per format version. Check the current export steps before starting; this product changed in 2024.
- **Build:** `raw.location_points`, `stg_visits`, `stg_trips`, visits and trips in `fct_life_events`, joins such as songs played on road trips, and a map on the day view.
- **Done when:** the day view shows where I was, what I played and my photos, with a map.

## Phase 5: front end and other people

- **Build:** Next.js timeline UI, a FastAPI layer over the marts, Postgres for app data (notes, accounts, upload status), an upload flow, Apple Music (privacy.apple.com) and YouTube Music (Takeout) adapters matched by ISRC.
- **Done when:** someone else can upload their exports and see their own timeline, and not mine.

## Shared model: `fct_life_events`

`user_id, event_id, event_type, source, started_at, ended_at, local_tz, place_id, lat, lon, ref_id`

A thin index over every event type. Each type keeps its own detailed fact table.

## Privacy

From phase 3 on, privacy is the main design constraint. Location and photos stay private or local. Anything public uses generated fake data.
