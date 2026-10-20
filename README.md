# Mallard

A personal data platform that costs nothing to run. Sources are loaded with dlt into a DuckLake (a Postgres catalog plus Parquet files in object storage), transformed with dbt-duckdb, orchestrated by Dagster on a scheduled GitHub Action, and published as a private dashboard.

```text
sources -> dlt -> DuckLake (Postgres catalog + Parquet on Cloudflare R2)
                     ^ dbt-duckdb (raw -> stage -> curate)
        headless Dagster on a scheduled GitHub Action
        -> Parquet export -> Observable Framework -> Cloudflare Pages behind Cloudflare Access
```

Work in progress: the lake works; sources come next. Progress is tracked in the [issues](https://github.com/jitsejan/mallard/issues).

## Setup

You need [uv](https://docs.astral.sh/uv/), a Postgres database for the catalog (a free Supabase project works), and a Cloudflare R2 bucket with an API token scoped to it.

```sh
uv sync
cp .env.example .env    # then fill in your own values
```

## Running the checks

```sh
uv run invoke lint                     # ruff and strict mypy
uv run invoke test                     # offline: tests marked `lake` skip
uv run --env-file .env invoke test     # also runs the tests against your lake
uv run invoke                          # lint, then test, as CI does
```

The `lake` tests create a uniquely named schema in your lake and drop it afterwards.
