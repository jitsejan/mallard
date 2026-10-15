"""The lake works end to end: DuckDB and dlt share one catalog and write Parquet to R2."""

from pathlib import Path

import dlt
import duckdb
import pytest

from mallard import lake

pytestmark = pytest.mark.lake

# DuckLake keeps small inserts in the catalog (about 10 rows by default) instead of writing
# Parquet, so a test that expects files needs well over that.
ROWS = 1000


def create_duck_table(con: duckdb.DuckDBPyConnection, schema: str) -> str:
    table = f"{lake.ALIAS}.{schema}.duck"
    con.execute(f"CREATE TABLE {table} AS SELECT i AS id, 'quack' AS word FROM range({ROWS}) t(i)")
    return table


def test_duckdb_round_trip(con: duckdb.DuckDBPyConnection, schema: str) -> None:
    table = create_duck_table(con, schema)

    assert con.execute(f"SELECT count(*), count(DISTINCT id) FROM {table}").fetchone() == (ROWS, ROWS)


def test_large_insert_writes_parquet_under_data_path(con: duckdb.DuckDBPyConnection, schema: str) -> None:
    create_duck_table(con, schema)

    files = con.execute(
        f"SELECT data_file FROM ducklake_list_files('{lake.ALIAS}', 'duck', schema => '{schema}')"
    ).fetchall()

    assert files, f"{ROWS} rows should be written as Parquet, not kept in the catalog"
    assert all(file.startswith(f"{lake.data_path()}{schema}/") for (file,) in files)


def test_dlt_load_is_visible_to_duckdb(con: duckdb.DuckDBPyConnection, schema: str, tmp_path: Path) -> None:
    # If dlt and DuckDB attached with different METADATA_SCHEMAs they would use two catalogs,
    # and DuckDB would not see this table.
    pipeline = dlt.pipeline(
        "smoke", destination=lake.dlt_destination(), dataset_name=schema, pipelines_dir=str(tmp_path)
    )
    pipeline.run([{"id": 1}, {"id": 2}], table_name="from_dlt", write_disposition="replace")

    assert con.execute(f"SELECT id FROM {lake.ALIAS}.{schema}.from_dlt ORDER BY id").fetchall() == [(1,), (2,)]
