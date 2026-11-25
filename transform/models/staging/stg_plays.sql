-- One row per music play, from every source, in one shape.
-- Phase 1: the export only. Phase 2 adds the API as a second CTE and a union.
with export as (

    select
        user_id,
        cast(ts as timestamptz)               as played_at,   -- export ts = when the stream ended
        spotify_track_uri                     as track_uri,
        master_metadata_track_name            as track_name,
        master_metadata_album_artist_name     as artist_name,
        master_metadata_album_album_name      as album_name,
        ms_played,
        coalesce(skipped, false)              as skipped,
        reason_start,
        reason_end,
        shuffle,
        platform,
        'spotify_export'                      as source
    from {{ source('raw', 'plays_export') }}
    where spotify_track_uri is not null       -- podcasts and audiobooks are out of scope

)

select
    *,
    timezone('Pacific/Auckland', played_at)   as played_at_nz,
    ms_played >= 30000                        as is_stream    -- Spotify counts 30s+ as a stream
from export
