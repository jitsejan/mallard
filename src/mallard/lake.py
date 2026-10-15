"""The one place that knows how to reach the lake. Everything reads credentials from env vars."""

import os
from urllib.parse import quote

import dlt

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


def pg_dsn() -> str:
    """libpq connection string for the Supabase catalog (used inside DuckDB's ATTACH)."""
    return (
        f"dbname={env('CATALOG_DB')} host={env('CATALOG_HOST')} port={env('CATALOG_PORT')} "
        f"user={env('CATALOG_USER')} password={env('CATALOG_PASSWORD')} sslmode=require"
    )


def pg_url() -> str:
    """Same catalog as a URL (used by dlt)."""
    user, password = quote(env("CATALOG_USER"), safe=""), quote(env("CATALOG_PASSWORD"), safe="")
    return f"postgres://{user}:{password}@{env('CATALOG_HOST')}:{env('CATALOG_PORT')}/{env('CATALOG_DB')}?sslmode=require"


def attach_statements() -> list[str]:
    """SQL that makes the lake available as database `lake` on a fresh DuckDB connection."""
    return [
        "INSTALL ducklake",
        "INSTALL postgres",
        "INSTALL httpfs",
        f"CREATE OR REPLACE SECRET r2 (TYPE S3, KEY_ID '{env('R2_KEY_ID')}', SECRET '{env('R2_SECRET')}', "
        f"ENDPOINT '{r2_host()}', REGION 'auto', URL_STYLE 'path')",
        f"ATTACH 'ducklake:postgres:{pg_dsn()}' AS {ALIAS} "
        f"(DATA_PATH '{data_path()}', METADATA_SCHEMA '{ALIAS}')",
    ]


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
