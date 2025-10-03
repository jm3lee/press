from __future__ import annotations

import pytest

from analytics_backend.db import DatabaseConfig


def _clear_standard_env(monkeypatch: pytest.MonkeyPatch) -> None:
    for var in [
        "DATABASE_HOST",
        "DATABASE_PORT",
        "DATABASE_USER",
        "DATABASE_PASSWORD",
        "DATABASE_NAME",
        "DATABASE_URL",
        "DATABASE_SSLMODE",
        "DATABASE_SSLROOTCERT",
        "DATABASE_SSLCERT",
        "DATABASE_SSLKEY",
        "DATABASE_SSLPASSWORD",
        "DATABASE_SSLCRL",
        "DATABASE_TARGET_SESSION_ATTRS",
    ]:
        monkeypatch.delenv(var, raising=False)


def test_from_env_includes_ssl_overrides(monkeypatch: pytest.MonkeyPatch) -> None:
    _clear_standard_env(monkeypatch)
    monkeypatch.setenv("DATABASE_HOST", "db.example.com")
    monkeypatch.setenv("DATABASE_USER", "analytics")
    monkeypatch.setenv("DATABASE_PASSWORD", "secret")
    monkeypatch.setenv("DATABASE_NAME", "analytics")
    monkeypatch.setenv("DATABASE_SSLMODE", "require")

    config = DatabaseConfig.from_env()

    params = config.connection_kwargs()
    assert params["host"] == "db.example.com"
    assert params["dbname"] == "analytics"
    assert params["sslmode"] == "require"


def test_from_env_parses_database_url_with_ssl(monkeypatch: pytest.MonkeyPatch) -> None:
    _clear_standard_env(monkeypatch)
    url = (
        "postgresql://username:password@db.example.com:25060/"
        "defaultdb?sslmode=require"
    )
    monkeypatch.setenv("DATABASE_URL", url)

    config = DatabaseConfig.from_env()

    assert config.host == "db.example.com"
    assert config.port == 25060
    assert config.database == "defaultdb"

    params = config.connection_kwargs()
    assert params["sslmode"] == "require"
    assert params["user"] == "username"
    assert params["password"] == "password"
