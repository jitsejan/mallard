"""The one place that knows how to reach the lake. Everything reads credentials from env vars."""

import os
from urllib.parse import quote

import dlt
import duckdb

ALIAS = "lake"


def env(name: str) -> str:
    value = os.environ.get(name)
    if not value:
        raise RuntimeError(f"Missing environment variable {name}")
    return value


def data_path() -> str:
    prefix = os.environ.get("R2_PREFIX", "").strip("/")
    return f"s3://{env('R2_BUCKET')}/{prefix}/" if prefix else f"s3://{env('R2_BUCKET')}/"


def r2_host() -> str:
    return f"{env('R2_ACCOUNT_ID')}.r2.cloudflarestorage.com"


def sql_literal(value: str) -> str:
    """A SQL string literal; doubling quotes keeps values like passwords from breaking the statement."""
    return "'" + value.replace("'", "''") + "'"


def pg_url() -> str:
    """Same catalog as a URL (used by dlt)."""
    user, password = quote(env("CATALOG_USER"), safe=""), quote(env("CATALOG_PASSWORD"), safe="")
    return (
        f"postgres://{user}:{password}@{env('CATALOG_HOST')}:{env('CATALOG_PORT')}/{env('CATALOG_DB')}?sslmode=require"
    )


def attach_statements() -> list[str]:
    """SQL that makes the lake available as database `lake` on a fresh DuckDB connection.

    Credentials go into secrets, never into the ATTACH path: DuckDB repeats that path in its error messages.
    """
    return [
        "INSTALL ducklake",
        "INSTALL postgres",
        "INSTALL httpfs",
        f"CREATE OR REPLACE SECRET r2 (TYPE S3, KEY_ID {sql_literal(env('R2_KEY_ID'))}, "
        f"SECRET {sql_literal(env('R2_SECRET'))}, ENDPOINT {sql_literal(r2_host())}, REGION 'auto', URL_STYLE 'path')",
        f"CREATE SECRET (TYPE postgres, HOST {sql_literal(env('CATALOG_HOST'))}, PORT {int(env('CATALOG_PORT'))}, "
        f"DATABASE {sql_literal(env('CATALOG_DB'))}, USER {sql_literal(env('CATALOG_USER'))}, "
        f"PASSWORD {sql_literal(env('CATALOG_PASSWORD'))})",
        f"ATTACH 'ducklake:postgres:sslmode=require' AS {ALIAS} "
        f"(DATA_PATH {sql_literal(data_path())}, METADATA_SCHEMA '{ALIAS}')",
    ]


def connect() -> duckdb.DuckDBPyConnection:
    """A fresh in-memory DuckDB connection with the lake attached."""
    con = duckdb.connect()
    for statement in attach_statements():
        con.execute(statement)
    return con


def dlt_destination() -> dlt.destinations.ducklake:
    """dlt reads its DuckLake settings from env vars with this prefix."""
    p = "DESTINATION__DUCKLAKE__CREDENTIALS__"
    os.environ[f"{p}DUCKLAKE_NAME"] = ALIAS
    os.environ[f"{p}CATALOG"] = pg_url()
    os.environ[f"{p}STORAGE__BUCKET_URL"] = data_path()
    os.environ[f"{p}STORAGE__CREDENTIALS__AWS_ACCESS_KEY_ID"] = env("R2_KEY_ID")
    os.environ[f"{p}STORAGE__CREDENTIALS__AWS_SECRET_ACCESS_KEY"] = env("R2_SECRET")
    os.environ[f"{p}STORAGE__CREDENTIALS__ENDPOINT_URL"] = f"https://{r2_host()}"
    os.environ[f"{p}STORAGE__CREDENTIALS__REGION_NAME"] = "auto"
    return dlt.destinations.ducklake()
