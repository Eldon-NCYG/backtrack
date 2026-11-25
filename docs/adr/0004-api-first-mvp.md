# 0004: API-first MVP, export backfill in phase 2

- **Status:** accepted
- **Date:** 2026-11-25
- **Changes:** the phase order in the original plan. [ADR 0003](0003-full-refresh-export-loader.md) still stands, for a loader that now arrives in phase 2.

## Context

There are two sources of plays. The export is a lifetime snapshot that Spotify takes days to deliver. The Web API returns the last 50 plays on request, and nothing older.

The original plan built phase 1 on the export and added the API sync in phase 2. That made the MVP a one-off file load, and left the incremental parts of the pipeline (auth, cursors, idempotent appends, scheduling) until the pipeline was already built.

## Decision

Phase 1 is built on the API alone. A sync pulls recently played every hour, run by launchd on my laptop, and the warehouse holds history from the first sync onward.

The export moves to phase 2 as a backfill. `stg_plays` then unions the two sources, and the export wins where they overlap.

## Alternatives considered

- **Export first (the original plan):** answers "June 2022" in phase 1, with richer fields (`ms_played`, `skipped`). But nothing can start until the export arrives, and the MVP has no schedule, state or incremental load in it.
- **Both in phase 1:** the full picture sooner, but the union and the overlap rule make the MVP roughly twice the size.
- **Hourly sync in the cloud from day one:** no gaps, but GitHub Actions keeps no data between runs, so S3 or MotherDuck would have to move into phase 1 too.

## Consequences

- Phase 1 can't answer "what was I listening to in June 2022?". That question is now phase 2's finish line. Phase 1's is "what did I play yesterday?".
- Phase 1 facts have no `ms_played`, `skipped` or stream flag. The API doesn't return them. They arrive with the export.
- The laptop sync will have gaps: the API forgets everything past 50 plays, and the laptop isn't always on. Gaps are flagged, not prevented, and the export fills them in phase 2.
- Phase 1 now depends on a Spotify developer app, which needs Premium, and on a refresh token that expires every 6 months.
- Data starts accumulating in week 2, so phase 2 has real overlap between the two sources to test the union against.
