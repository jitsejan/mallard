# Mallard

[![CI](https://github.com/jitsejan/mallard/actions/workflows/ci.yml/badge.svg?branch=main)](https://github.com/jitsejan/mallard/actions/workflows/ci.yml)
[![codecov](https://codecov.io/gh/jitsejan/mallard/graph/badge.svg)](https://codecov.io/gh/jitsejan/mallard)
[![Python](https://img.shields.io/python/required-version-toml?tomlFilePath=https%3A%2F%2Fraw.githubusercontent.com%2Fjitsejan%2Fmallard%2Fmain%2Fpyproject.toml)](pyproject.toml)
[![License: MIT](https://img.shields.io/badge/license-MIT-blue)](LICENSE)
[![Ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json)](https://github.com/astral-sh/ruff)
[![uv](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/uv/main/assets/badge/v0.json)](https://github.com/astral-sh/uv)

A personal data platform that costs nothing to run. Sources are loaded with dlt into a DuckLake (a Postgres catalog plus Parquet files in object storage), transformed with dbt-duckdb, orchestrated by Dagster on a scheduled GitHub Action, and published as a private dashboard.

```text
sources -> dlt -> DuckLake (Postgres catalog + Parquet on Cloudflare R2)
                     ^ dbt-duckdb (raw -> stage -> curate)
        headless Dagster on a scheduled GitHub Action
        -> Parquet export -> Observable Framework -> Cloudflare Pages behind Cloudflare Access
```

Work in progress: the lake works and the guardrails are in place; sources come next. Progress is tracked in the [issues](https://github.com/jitsejan/mallard/issues).

## Setup

You need [uv](https://docs.astral.sh/uv/), a Postgres database for the catalog (a free Supabase project works), and a Cloudflare R2 bucket with an API token scoped to it.

```sh
uv sync
cp .env.example .env         # then fill in your own values
uv run pre-commit install    # lint on commit, tests on push, secrets blocked
```

## Running the checks

```sh
uv run invoke lint                     # ruff and strict mypy
uv run invoke audit                    # known vulnerabilities in locked dependencies
uv run invoke test                     # offline: tests marked `lake` skip
uv run --env-file .env invoke test     # also runs the tests against your lake
uv run invoke                          # lint, audit, then test, as CI does
```

Tests fail below 95% coverage, measured offline with branch coverage. The `lake` tests create a uniquely named schema in your lake and drop it afterwards.

## How changes get in

Every change starts from an issue and reaches `main` through a pull request with a passing CI check: lint, audit, tests with the coverage floor, and the pre-commit hooks, including gitleaks. Dependabot proposes dependency and action updates weekly. [CLAUDE.md](CLAUDE.md) holds the full working agreement.

## License

[MIT](LICENSE)
