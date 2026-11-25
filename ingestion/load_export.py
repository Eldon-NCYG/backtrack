"""Backfill loader: Spotify extended streaming history -> raw zone (Parquet) -> raw.plays_export.

Contract (same for every loader in this folder):
- input: raw files from one source
- output: one raw table in the warehouse
- safe to re-run: the same input always produces the same table
- prints row count and date range

This loader does a full refresh. The export is a complete lifetime snapshot of
around 100k-200k rows, so rebuilding it takes seconds and avoids any
incremental-state bugs.
"""

from __future__ import annotations

import glob
import os
import shutil
from pathlib import Path

import duckdb

DROP_COLUMNS = {"ip_addr"}  # personal data we never store


def load_export(
    export_glob: str,
    raw_root: str,
    warehouse: str,
    user_id: int = 1,
) -> tuple[int, str | None, str | None]:
    files = sorted(glob.glob(export_glob))
    if not files:
        raise FileNotFoundError(f"No export files match {export_glob!r}")

    Path(warehouse).parent.mkdir(parents=True, exist_ok=True)
    con = duckdb.connect(warehouse)
    con.execute("create schema if not exists raw")

    source = f"read_json({files!r}, format = 'array', union_by_name = true)"

    # Build the column list without the columns we must never store.
    # Done in Python so it works whether or not a file contains ip_addr.
    columns = [row[0] for row in con.execute(f"describe select * from {source}").fetchall()]
    keep = ", ".join(f'"{c}"' for c in columns if c not in DROP_COLUMNS)

    # 1. Land a cleaned copy in the raw zone, partitioned by year.
    #    The folder is cleared first so a re-run never leaves stale files behind.
    export_dir = Path(raw_root) / "source=export"
    shutil.rmtree(export_dir, ignore_errors=True)
    export_dir.mkdir(parents=True, exist_ok=True)
    con.execute(
        f"""
        copy (
            select {keep},
                   year(cast(ts as timestamp)) as year
            from {source}
        )
        to '{export_dir.as_posix()}' (format parquet, partition_by (year))
        """
    )

    # 2. Rebuild the raw table from the raw zone, so the warehouse can always be
    #    recreated from files alone.
    con.execute(
        f"""
        create or replace table raw.plays_export as
        select
            {int(user_id)} as user_id,
            * exclude (year),
            current_timestamp as _loaded_at
        from read_parquet('{export_dir.as_posix()}/*/*.parquet', hive_partitioning = true)
        """
    )

    rows, first, last = con.execute(
        "select count(*), min(ts)::varchar, max(ts)::varchar from raw.plays_export"
    ).fetchone()
    con.close()
    return rows, first, last


def main() -> None:
    rows, first, last = load_export(
        export_glob=os.environ.get("EXPORT_GLOB", "data/export/Streaming_History_Audio_*.json"),
        raw_root=os.environ.get("RAW_ROOT", "data/raw"),
        warehouse=os.environ.get("WAREHOUSE", "data/listening.duckdb"),
        user_id=int(os.environ.get("USER_ID", "1")),
    )
    print(f"raw.plays_export: {rows:,} plays from {first} to {last}")


if __name__ == "__main__":
    main()
