# Data sources

Phase 1 uses the Web API only. The export arrives in phase 2 as a backfill ([ADR 0004](adr/0004-api-first-mvp.md)).

## Spotify Web API: recently played (phase 1)

- `GET /v1/me/player/recently-played`, scope `user-read-recently-played`. Setup: [the runbook](runbooks/spotify-api-setup.md).
- Returns at most the **last 50 plays** (`limit` defaults to 20, so ask for 50). `before` and `after` (Unix ms) only move within those 50, one per request. It can't backfill.
- Each item has `played_at` (UTC), a full `track` object and a `context` (playlist, album, artist, or null).
- No `ms_played`, `skipped` or `reason_end`. Music only: the endpoint doesn't return podcast episodes.
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
  "cursors": { "after": "1795554300000", "before": "1795554000000" }
}
```

### Access and limits

Checked against Spotify's developer docs on 2026-11-25. Spotify tightened development mode in February 2026, so re-check before relying on anything not listed here.

- A personal app runs in **development mode**: the owner needs Spotify Premium, one app per developer, up to five authorised users. If Premium lapses the app stops working.
- Auth is the OAuth authorization code flow. Access tokens last 1 hour. The **refresh token lasts 6 months** from the day I approve the app, and refreshing doesn't extend it.
- A loopback redirect URI must use `http://127.0.0.1:<port>`. `localhost` is rejected.
- Development mode no longer returns track `popularity`, or artist `popularity` and `followers`. `external_ids` (ISRC) is still returned.
- The batch endpoints (`GET /tracks?ids=`, `GET /artists?ids=`) are gone. Lookups are one request per item.

## Spotify extended streaming history (export, phase 2)

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

## What each source gives

| | API (phase 1) | Export (phase 2) |
|---|---|---|
| Reach | Last 50 plays | Account lifetime |
| Arrives | On request | Days after asking |
| Play time | `played_at` | `ts` (stream end) |
| How long I listened | No, only the track's `duration_ms` | `ms_played` |
| Skips, shuffle, start and end reasons | No | Yes |
| Track, artist and album IDs, ISRC | Yes | Track URI and names only |
| Podcasts | No | Yes (excluded in staging) |

## Open questions

- Does API `played_at` mark the start or the end of a play? The docs only say when the track was played. Before building the phase 2 union in `stg_plays`, compare plays that appear in both sources and record the answer in an ADR.
- Does the API leave out very short plays that the export keeps? Check the same way.
