# Data sources

## Spotify extended streaming history (export)

- Requested from Spotify's privacy settings, under Download your data → **Extended streaming history**. Covers the lifetime of the account and takes days to arrive. See [the runbook](runbooks/request-spotify-export.md).
- Files: `Streaming_History_Audio_*.json`, each a JSON array with one object per play.
- `ts` is when the stream ended, in UTC.
- Real files also contain `ip_addr` (dropped by the loader and never stored), podcast and audiobook fields (null track fields), and `offline_timestamp`.

```json
{
  "ts": "2026-11-24T21:05:00Z",
  "ms_played": 213573,
  "platform": "iOS 18.1 (iPhone16,1)",
  "conn_country": "NZ",
  "master_metadata_track_name": "Never Gonna Give You Up",
  "master_metadata_album_artist_name": "Rick Astley",
  "master_metadata_album_album_name": "Whenever You Need Somebody",
  "spotify_track_uri": "spotify:track:4cOdK2wGLETKBW3PvgPWqT",
  "reason_start": "trackdone",
  "reason_end": "trackdone",
  "shuffle": false,
  "skipped": false,
  "offline": false,
  "incognito_mode": false
}
```

## Spotify Web API: recently played (phase 2)

- `GET /v1/me/player/recently-played`, scope `user-read-recently-played`.
- Returns at most the **last 50 plays**. `before` and `after` (Unix ms) only move within those 50, one per request. It can't backfill.
- Each item has `played_at` (UTC), a full `track` object and a `context` (playlist, album, artist, or null).
- No `ms_played`, `skipped` or `reason_end`.
- Keep `track.external_ids.isrc`. It's the key for matching songs across services in phase 5.

```json
{
  "items": [{
    "played_at": "2026-11-24T21:05:00.000Z",
    "track": {
      "id": "4cOdK2wGLETKBW3PvgPWqT",
      "name": "Never Gonna Give You Up",
      "duration_ms": 213573,
      "external_ids": { "isrc": "GBARL9300135" },
      "artists": [{ "id": "0gxyHStUsqpMadRV0Di1Qt", "name": "Rick Astley" }],
      "album": { "id": "6N9PS4QXF1D0OWPk0SXTb4", "name": "Whenever You Need Somebody" }
    },
    "context": { "type": "playlist", "uri": "spotify:playlist:37i9dQZF1DXcBWIGoYBM5M" }
  }],
  "cursors": { "after": "1732482300000", "before": "1732482000000" }
}
```

## Open question

Does API `played_at` mark the start or the end of a play? The docs only say "when the track was played". Before building the phase 2 union in `stg_plays`, compare plays that appear in both sources and record the answer in an ADR.
