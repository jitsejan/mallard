"""Credentials reach the catalog intact and never show up in error messages."""

import duckdb
import pytest

from mallard import lake


def test_failed_connection_does_not_show_the_password(fake_lake_env: None) -> None:
    # Error messages end up in public GitHub Action logs.
    with pytest.raises(duckdb.IOException) as error:
        lake.connect()

    assert "fake-password-123" not in str(error.value)


def test_password_with_a_space_and_a_quote_still_reaches_postgres(
    fake_lake_env: None, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setenv("CATALOG_PASSWORD", "fake pass'word")

    # A connection error means the password got through intact; a parser error would mean it broke the SQL.
    with pytest.raises(duckdb.IOException):
        lake.connect()
