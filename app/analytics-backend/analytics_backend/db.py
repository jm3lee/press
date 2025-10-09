"""Database utilities for the analytics backend."""

from __future__ import annotations

import os
from contextlib import contextmanager
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Dict, Iterable, List, Sequence

from psycopg2.extras import Json, execute_values
from psycopg2.pool import SimpleConnectionPool
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
    """Runtime configuration for TimescaleDB connectivity."""

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


class TimescaleDB:
    """Connection pool wrapper for TimescaleDB."""

    def __init__(self, config: DatabaseConfig) -> None:
        self._config = config
        self._pool = SimpleConnectionPool(
            config.minconn,
            config.maxconn,
            **config.connection_kwargs(),
        )

    @contextmanager
    def connection(self):
        conn = self._pool.getconn()
        try:
            yield conn
        finally:
            self._pool.putconn(conn)

    def close(self) -> None:
        self._pool.closeall()

    def initialize(self) -> None:
        """Ensure the TimescaleDB schema is available."""

        with self.connection() as conn:  # type: ignore[assignment]
            with conn.cursor() as cur:
                cur.execute("CREATE EXTENSION IF NOT EXISTS timescaledb")
                cur.execute(
                    """
                    CREATE TABLE IF NOT EXISTS engagement_events (
                        id BIGSERIAL NOT NULL,
                        site TEXT NOT NULL,
                        session_id UUID NOT NULL,
                        event_type TEXT NOT NULL,
                        target TEXT NOT NULL,
                        occurred_at TIMESTAMPTZ NOT NULL,
                        meta JSONB NOT NULL,
                        received_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
                        PRIMARY KEY (occurred_at, id)
                    )
                    """
                )
                cur.execute(
                    "SELECT create_hypertable('engagement_events', 'occurred_at', "
                    "if_not_exists => TRUE)"
                )
            conn.commit()

    def insert_events(
        self,
        site: str,
        session_id: str,
        events: Iterable[Dict[str, Any]],
    ) -> int:
        """Persist a batch of events in a single transaction."""

        rows: List[Sequence[Any]] = []
        for event in events:
            rows.append(
                (
                    site,
                    session_id,
                    event["event_type"],
                    event["target"],
                    _parse_timestamp(event.get("occurred_at")),
                    Json(event.get("meta", {})),
                )
            )

        if not rows:
            return 0

        with self.connection() as conn:  # type: ignore[assignment]
            with conn.cursor() as cur:
                execute_values(
                    cur,
                    """
                    INSERT INTO engagement_events (
                        site,
                        session_id,
                        event_type,
                        target,
                        occurred_at,
                        meta
                    ) VALUES %s
                    """,
                    rows,
                )
            conn.commit()
        return len(rows)

    def truncate_events(self) -> None:
        with self.connection() as conn:  # type: ignore[assignment]
            with conn.cursor() as cur:
                cur.execute("TRUNCATE engagement_events")
            conn.commit()

    def fetch_recent_events(self, limit: int = 25) -> List[Dict[str, Any]]:
        limit = max(1, min(limit, 200))
        with self.connection() as conn:  # type: ignore[assignment]
            with conn.cursor() as cur:
                cur.execute(
                    """
                    SELECT
                        id,
                        site,
                        session_id,
                        event_type,
                        target,
                        occurred_at,
                        meta,
                        received_at
                    FROM engagement_events
                    ORDER BY received_at DESC
                    LIMIT %s
                    """,
                    (limit,),
                )
                rows = cur.fetchall()

        events: List[Dict[str, Any]] = []
        for row in rows:
            occurred_at = row[5]
            received_at = row[7]
            events.append(
                {
                    "id": row[0],
                    "site": row[1],
                    "session_id": row[2],
                    "event_type": row[3],
                    "target": row[4],
                    "occurred_at": _parse_timestamp(occurred_at).isoformat(),
                    "meta": row[6] or {},
                    "received_at": _parse_timestamp(received_at).isoformat(),
                }
            )
        return events


def _parse_timestamp(value: Any) -> datetime:
    if isinstance(value, datetime):
        if value.tzinfo is None:
            return value.replace(tzinfo=timezone.utc)
        return value.astimezone(timezone.utc)
    if isinstance(value, str):
        # Accept RFC3339/ISO-8601 strings with or without timezone suffix.
        cleaned = value.replace("Z", "+00:00")
        parsed = datetime.fromisoformat(cleaned)
        if parsed.tzinfo is None:
            parsed = parsed.replace(tzinfo=timezone.utc)
        return parsed.astimezone(timezone.utc)
    return datetime.now(tz=timezone.utc)
