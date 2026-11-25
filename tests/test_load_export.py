from pathlib import Path

import duckdb

from ingestion.fake_export import generate, write_files
from ingestion.load_export import load_export


def _run(tmp_path: Path, n: int = 1500):
    export = tmp_path / "export"
    write_files(generate(n), export, per_file=500)
    warehouse = tmp_path / "test.duckdb"
    result = load_export(
        export_glob=str(export / "Streaming_History_Audio_*.json"),
        raw_root=str(tmp_path / "raw"),
        warehouse=str(warehouse),
    )
    return result, warehouse


def test_loads_every_play(tmp_path):
    (rows, first, last), _ = _run(tmp_path)
    assert rows == 1500
    assert first < last


def test_ip_addr_is_never_stored(tmp_path):
    _, warehouse = _run(tmp_path)
    con = duckdb.connect(str(warehouse))
    cols = {r[0] for r in con.execute("describe raw.plays_export").fetchall()}
    assert "ip_addr" not in cols
    raw_cols = {
        r[0]
        for r in con.execute(
            f"describe select * from read_parquet('{tmp_path}/raw/source=export/*/*.parquet')"
        ).fetchall()
    }
    assert "ip_addr" not in raw_cols


def test_rerun_is_idempotent(tmp_path):
    (rows_1, _, _), _ = _run(tmp_path)
    (rows_2, _, _), _ = _run(tmp_path)
    assert rows_1 == rows_2 == 1500


def test_user_id_is_set(tmp_path):
    _, warehouse = _run(tmp_path)
    con = duckdb.connect(str(warehouse))
    assert con.execute("select distinct user_id from raw.plays_export").fetchall() == [(1,)]
