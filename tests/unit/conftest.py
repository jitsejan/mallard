"""Fixtures for unit tests: fake credentials only, nothing reaches the real lake."""

import pytest

FAKE_ENV = {
    # Nothing listens on port 1, so every connection attempt fails straight away.
    "CATALOG_HOST": "127.0.0.1",
    "CATALOG_PORT": "1",
    "CATALOG_DB": "postgres",
    "CATALOG_USER": "fake-user",
    "CATALOG_PASSWORD": "fake-password-123",
    "R2_ACCOUNT_ID": "fake-account",
    "R2_KEY_ID": "fake-key-id",
    "R2_SECRET": "fake-r2-secret",
    "R2_BUCKET": "lake",
    "R2_PREFIX": "mallard/",
}


@pytest.fixture
def fake_lake_env(monkeypatch: pytest.MonkeyPatch) -> None:
    """Point the lake module at fake credentials; monkeypatch restores the real environment afterwards."""
    for name, value in FAKE_ENV.items():
        monkeypatch.setenv(name, value)
