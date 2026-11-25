# 0003: Full refresh for the export loader

- **Status:** accepted
- **Date:** 2026-11-25
- **Note:** the export loader moved from phase 1 to phase 2 under [ADR 0004](0004-api-first-mvp.md). The decision is unchanged.

## Context

The export is a complete lifetime snapshot. A newer export contains everything an older one does, plus more.

## Decision

`load_export.py` rebuilds the raw zone folder and `raw.plays_export` from scratch on every run.

## Alternatives considered

- **Incremental append:** loading a second export would double-count plays unless every row is deduplicated, and it needs state to track what's been loaded.
- **Merge on a key:** works, but plays have no natural unique ID, so the key would be a guess (`ts` + track URI).

## Consequences

- Idempotent by design. The same files always give the same table. Takes seconds at this size.
- Wouldn't scale to billions of rows, which this project will never have. The API sync is incremental because it is a stream, not a snapshot.
