"""Database configuration helpers shared across backend services."""

from __future__ import annotations

import os
from dataclasses import dataclass, field
from typing import Any, Dict
from urllib.parse import parse_qs, urlparse


def _required_env(var: str) -> str:
    value = os.getenv(var)
    if not value:
        raise RuntimeError(f"Environment variable {var} must be set")
    return value


def _apply_optional_ssl_env(options: Dict[str, Any]) -> None:
    """Inject SSL-related overrides from the environment if present."""

    ssl_env_map = {
        "DATABASE_SSLMODE": "sslmode",
        "DATABASE_SSLROOTCERT": "sslrootcert",
        "DATABASE_SSLCERT": "sslcert",
        "DATABASE_SSLKEY": "sslkey",
        "DATABASE_SSLPASSWORD": "sslpassword",
        "DATABASE_SSLCRL": "sslcrl",
        "DATABASE_TARGET_SESSION_ATTRS": "target_session_attrs",
    }

    for env_var, option_name in ssl_env_map.items():
        value = os.getenv(env_var)
        if value:
            options[option_name] = value


@dataclass
class DatabaseConfig:
    """Runtime configuration for PostgreSQL connectivity."""

    host: str
    port: int
    user: str
    password: str
    database: str
    minconn: int = 1
    maxconn: int = 10
    options: Dict[str, Any] = field(default_factory=dict)

    @classmethod
    def from_env(cls) -> "DatabaseConfig":
        """Construct a configuration instance from environment variables."""

        minconn = int(os.getenv("DATABASE_POOL_MIN", "1"))
        maxconn = int(os.getenv("DATABASE_POOL_MAX", "10"))

        database_url = os.getenv("DATABASE_URL")
        if database_url:
            return cls._from_url(database_url, minconn=minconn, maxconn=maxconn)

        host = _required_env("DATABASE_HOST")
        port = int(os.getenv("DATABASE_PORT", "5432"))
        user = _required_env("DATABASE_USER")
        password = _required_env("DATABASE_PASSWORD")
        database = _required_env("DATABASE_NAME")

        options: Dict[str, Any] = {}
        _apply_optional_ssl_env(options)

        return cls(
            host=host,
            port=port,
            user=user,
            password=password,
            database=database,
            minconn=minconn,
            maxconn=maxconn,
            options=options,
        )

    @classmethod
    def _from_url(
        cls, url: str, *, minconn: int, maxconn: int
    ) -> "DatabaseConfig":
        """Create a configuration object from a PostgreSQL connection URL."""

        parsed = urlparse(url)
        if parsed.scheme not in {"postgres", "postgresql"}:
            raise RuntimeError("DATABASE_URL must use the postgres scheme")
        if not parsed.hostname:
            raise RuntimeError("DATABASE_URL must include a hostname")

        database = parsed.path.lstrip("/") or None
        if not database:
            raise RuntimeError("DATABASE_URL must include a database name")

        query_params = {
            key: values[-1]
            for key, values in parse_qs(parsed.query, keep_blank_values=True).items()
            if values
        }

        options: Dict[str, Any] = {}
        options.update(query_params)
        _apply_optional_ssl_env(options)

        return cls(
            host=parsed.hostname,
            port=parsed.port or 5432,
            user=parsed.username or "",
            password=parsed.password or "",
            database=database,
            minconn=minconn,
            maxconn=maxconn,
            options=options,
        )

    def connection_kwargs(self) -> Dict[str, Any]:
        """Return psycopg connection keyword arguments."""

        params: Dict[str, Any] = {
            "host": self.host,
            "port": self.port,
            "user": self.user,
            "password": self.password,
            "dbname": self.database,
        }
        params.update(self.options)
        return params


__all__ = ["DatabaseConfig"]
