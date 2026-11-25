"""Generate a fake Spotify extended streaming history export.

Used for local development before the real export arrives, for CI, and for any
public demo. It mimics the real file layout and field names, including the
awkward parts: podcast rows with null track fields, short plays, skips and an
ip_addr field that the loader must drop.

    python -m ingestion.fake_export --out data/export --plays 5000
"""

from __future__ import annotations

import argparse
import json
import random
import string
from datetime import UTC, datetime, timedelta
from pathlib import Path

ARTISTS = [f"Fake Artist {i:02d}" for i in range(1, 41)]
PLATFORMS = ["iOS 18.1 (iPhone16,1)", "osx", "windows", "web_player", "android"]
REASONS_END = ["trackdone", "fwdbtn", "endplay", "logout", "backbtn"]


def _uri(rng: random.Random, kind: str) -> str:
    alphabet = string.ascii_letters + string.digits
    return f"spotify:{kind}:" + "".join(rng.choice(alphabet) for _ in range(22))


def build_catalogue(rng: random.Random, n_tracks: int = 400) -> list[dict]:
    tracks = []
    for i in range(n_tracks):
        artist = rng.choice(ARTISTS)
        tracks.append(
            {
                "name": f"Fake Song {i:03d}",
                "artist": artist,
                "album": f"{artist} Album {rng.randint(1, 4)}",
                "uri": _uri(rng, "track"),
                "duration_ms": rng.randint(120_000, 320_000),
            }
        )
    return tracks


def generate(n_plays: int, seed: int = 42) -> list[dict]:
    rng = random.Random(seed)
    tracks = build_catalogue(rng)
    start = datetime(2019, 3, 1, tzinfo=UTC)
    end = datetime(2026, 10, 31, tzinfo=UTC)
    span = (end - start).total_seconds()

    plays = []
    for _ in range(n_plays):
        ended = start + timedelta(seconds=rng.random() * span)
        is_podcast = rng.random() < 0.04
        base = {
            "ts": ended.strftime("%Y-%m-%dT%H:%M:%SZ"),
            "platform": rng.choice(PLATFORMS),
            "conn_country": "NZ",
            "ip_addr": f"203.0.113.{rng.randint(1, 254)}",  # documentation range, not real
            "reason_start": rng.choice(["trackdone", "clickrow", "fwdbtn"]),
            "shuffle": rng.random() < 0.4,
            "offline": rng.random() < 0.05,
            "offline_timestamp": None,
            "incognito_mode": False,
        }
        if is_podcast:
            base.update(
                {
                    "ms_played": rng.randint(60_000, 3_000_000),
                    "master_metadata_track_name": None,
                    "master_metadata_album_artist_name": None,
                    "master_metadata_album_album_name": None,
                    "spotify_track_uri": None,
                    "episode_name": "Fake Episode",
                    "episode_show_name": "Fake Podcast",
                    "spotify_episode_uri": _uri(rng, "episode"),
                    "reason_end": "endplay",
                    "skipped": False,
                }
            )
        else:
            t = rng.choice(tracks)
            skipped = rng.random() < 0.18
            ms = rng.randint(1_000, 29_000) if skipped else rng.randint(30_000, t["duration_ms"])
            base.update(
                {
                    "ms_played": ms,
                    "master_metadata_track_name": t["name"],
                    "master_metadata_album_artist_name": t["artist"],
                    "master_metadata_album_album_name": t["album"],
                    "spotify_track_uri": t["uri"],
                    "episode_name": None,
                    "episode_show_name": None,
                    "spotify_episode_uri": None,
                    "reason_end": "fwdbtn" if skipped else rng.choice(REASONS_END),
                    "skipped": skipped,
                }
            )
        plays.append(base)

    plays.sort(key=lambda p: p["ts"])
    return plays


def write_files(plays: list[dict], out: Path, per_file: int = 2000) -> list[Path]:
    """Split into files named like the real export."""
    out.mkdir(parents=True, exist_ok=True)
    paths = []
    for idx in range(0, len(plays), per_file):
        chunk = plays[idx : idx + per_file]
        y0, y1 = chunk[0]["ts"][:4], chunk[-1]["ts"][:4]
        path = out / f"Streaming_History_Audio_{y0}-{y1}_{idx // per_file}.json"
        path.write_text(json.dumps(chunk, indent=2))
        paths.append(path)
    return paths


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out", default="data/export")
    parser.add_argument("--plays", type=int, default=5000)
    parser.add_argument("--seed", type=int, default=42)
    args = parser.parse_args()
    paths = write_files(generate(args.plays, args.seed), Path(args.out))
    print(f"wrote {args.plays:,} fake plays to {len(paths)} files in {args.out}")


if __name__ == "__main__":
    main()
