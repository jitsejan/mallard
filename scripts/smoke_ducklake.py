"""Write and read a table through DuckDB and through dlt, then clean up.

set -a; source .env; set +a
uv run python -m scripts.smoke_ducklake
"""

import dlt

from mallard import lake

SCHEMA = "smoke_test"


def main() -> None:
    print("1. attach lake")
    con = lake.connect()

    print("2. write and read through DuckDB")
    con.execute(f"CREATE SCHEMA IF NOT EXISTS {lake.ALIAS}.{SCHEMA}")
    con.execute(
        f"CREATE OR REPLACE TABLE {lake.ALIAS}.{SCHEMA}.duck AS SELECT i AS id, 'quack' AS word FROM range(1000) t(i)"
    )
    assert con.execute(f"SELECT count(*) FROM {lake.ALIAS}.{SCHEMA}.duck").fetchone()[0] == 1000

    print("3. parquet file registered?")
    files = con.execute(
        f"SELECT data_file FROM ducklake_list_files('{lake.ALIAS}', 'duck', schema => '{SCHEMA}')"
    ).fetchall()
    assert files, "no parquet files"
    print("  ", files[0][0])
    con.close()

    print("4. load through dlt")
    pipeline = dlt.pipeline("smoke", destination=lake.dlt_destination(), dataset_name=SCHEMA)
    pipeline.run([{"id": 1}], table_name="from_dlt", write_disposition="replace")

    print("5. read the dlt table back, then clean up")
    con = lake.connect()
    assert con.execute(f"SELECT count(*) FROM {lake.ALIAS}.{SCHEMA}.from_dlt").fetchone()[0] == 1
    con.execute(f"DROP SCHEMA {lake.ALIAS}.{SCHEMA} CASCADE")

    print("Lake works end to end.")


if __name__ == "__main__":
    main()
