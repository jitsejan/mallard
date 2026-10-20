"""How the lake module turns environment variables into paths, URLs and dlt settings."""

import os
from urllib.parse import unquote, urlsplit

import dlt
import pytest

from mallard import lake

DLT_PREFIX = "DESTINATION__DUCKLAKE__CREDENTIALS__"


def test_env_returns_the_value(fake_lake_env: None) -> None:
    assert lake.env("R2_BUCKET") == "lake"


@pytest.mark.parametrize("value", [None, ""])
def test_env_rejects_a_missing_or_empty_variable(
    fake_lake_env: None, monkeypatch: pytest.MonkeyPatch, value: str | None
) -> None:
    if value is None:
        monkeypatch.delenv("R2_BUCKET")
    else:
        monkeypatch.setenv("R2_BUCKET", value)

    with pytest.raises(RuntimeError, match="R2_BUCKET"):
        lake.env("R2_BUCKET")


@pytest.mark.parametrize(
    ("prefix", "expected"),
    [
        ("mallard/", "s3://lake/mallard/"),
        ("mallard", "s3://lake/mallard/"),
        ("/mallard/", "s3://lake/mallard/"),
        ("team/mallard", "s3://lake/team/mallard/"),
        ("", "s3://lake/"),
        (None, "s3://lake/"),
    ],
)
def test_data_path_always_ends_in_one_slash(
    fake_lake_env: None, monkeypatch: pytest.MonkeyPatch, prefix: str | None, expected: str
) -> None:
    if prefix is None:
        monkeypatch.delenv("R2_PREFIX")
    else:
        monkeypatch.setenv("R2_PREFIX", prefix)

    assert lake.data_path() == expected


def test_r2_host_uses_the_account_id(fake_lake_env: None) -> None:
    assert lake.r2_host() == "fake-account.r2.cloudflarestorage.com"


@pytest.mark.parametrize("password", ["plain", "with space", "p@ss:w/rd?#", "quo'te", "100%"])
def test_pg_url_keeps_any_password_intact(fake_lake_env: None, monkeypatch: pytest.MonkeyPatch, password: str) -> None:
    monkeypatch.setenv("CATALOG_PASSWORD", password)

    url = urlsplit(lake.pg_url())

    assert url.password is not None and unquote(url.password) == password
    assert (url.hostname, url.port, url.path) == ("127.0.0.1", 1, "/postgres")


def test_dlt_destination_points_dlt_at_the_lake(fake_lake_env: None, monkeypatch: pytest.MonkeyPatch) -> None:
    expected = {
        "DUCKLAKE_NAME": "lake",
        "CATALOG": lake.pg_url(),
        "STORAGE__BUCKET_URL": "s3://lake/mallard/",
        "STORAGE__CREDENTIALS__AWS_ACCESS_KEY_ID": "fake-key-id",
        "STORAGE__CREDENTIALS__AWS_SECRET_ACCESS_KEY": "fake-r2-secret",
        "STORAGE__CREDENTIALS__ENDPOINT_URL": "https://fake-account.r2.cloudflarestorage.com",
        "STORAGE__CREDENTIALS__REGION_NAME": "auto",
    }
    # dlt_destination() writes to os.environ; deleting first makes monkeypatch remove its values afterwards.
    for setting in expected:
        monkeypatch.delenv(DLT_PREFIX + setting, raising=False)

    destination = lake.dlt_destination()

    assert isinstance(destination, dlt.destinations.ducklake)
    assert {setting: os.environ[DLT_PREFIX + setting] for setting in expected} == expected
