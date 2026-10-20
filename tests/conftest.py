"""Shared fixtures. Tests marked `lake` skip unless the lake credentials are set."""

import os
import uuid
from collections.abc import Iterator

import duckdb
import pytest

from mallard import lake

LAKE_VARS = (
    "CATALOG_HOST",
    "CATALOG_PORT",
    "CATALOG_DB",
    "CATALOG_USER",
    "CATALOG_PASSWORD",
    "R2_ACCOUNT_ID",
    "R2_KEY_ID",
    "R2_SECRET",
    "R2_BUCKET",
)


def pytest_collection_modifyitems(items: list[pytest.Item]) -> None:
    missing = [name for name in LAKE_VARS if not os.environ.get(name)]
    if not missing:
        return
    skip = pytest.mark.skip(reason=f"lake credentials missing: {', '.join(missing)}")
    for item in items:
        if item.get_closest_marker("lake"):
            item.add_marker(skip)


@pytest.fixture(scope="module")
def con() -> Iterator[duckdb.DuckDBPyConnection]:
    # Module scope because attaching the lake downloads extensions and connects to Postgres.
    connection = lake.connect()
    yield connection
    connection.close()


@pytest.fixture
def schema(con: duckdb.DuckDBPyConnection) -> Iterator[str]:
    """An empty schema in the lake, dropped afterwards even when the test fails."""
    name = f"test_{uuid.uuid4().hex[:8]}"
    con.execute(f"CREATE SCHEMA {lake.ALIAS}.{name}")
    yield name
    con.execute(f"DROP SCHEMA {lake.ALIAS}.{name} CASCADE")
