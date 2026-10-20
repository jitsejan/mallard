"""The lake module with fake credentials: nothing here reaches the real lake."""

import duckdb
import pytest

from mallard import lake

FAKE_ENV = {
    # Nothing listens on port 1, so every connection attempt fails straight away.
    "CATALOG_HOST": "127.0.0.1",
    "CATALOG_PORT": "1",
    "CATALOG_DB": "postgres",
    "CATALOG_USER": "fake-user",
    "R2_ACCOUNT_ID": "fake-account",
    "R2_KEY_ID": "fake-key-id",
    "R2_SECRET": "fake-r2-secret",
    "R2_BUCKET": "lake",
    "R2_PREFIX": "mallard/",
}


@pytest.fixture
def unreachable_lake(monkeypatch: pytest.MonkeyPatch) -> None:
    for name, value in FAKE_ENV.items():
        monkeypatch.setenv(name, value)


def test_failed_connection_does_not_show_the_password(unreachable_lake: None, monkeypatch: pytest.MonkeyPatch) -> None:
    # Error messages end up in public GitHub Action logs.
    monkeypatch.setenv("CATALOG_PASSWORD", "fake-password-123")

    with pytest.raises(duckdb.IOException) as error:
        lake.connect()

    assert "fake-password-123" not in str(error.value)


def test_password_with_a_space_and_a_quote_still_reaches_postgres(
    unreachable_lake: None, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setenv("CATALOG_PASSWORD", "fake pass'word")

    # A connection error means the password got through intact; a parser error would mean it broke the SQL.
    with pytest.raises(duckdb.IOException):
        lake.connect()
