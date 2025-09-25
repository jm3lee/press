"""Database utilities for the analytics backend."""

from __future__ import annotations

import os
from contextlib import contextmanager
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any, Dict, Iterable, List, Sequence

from psycopg2.extras import Json, execute_values
from psycopg2.pool import SimpleConnectionPool


def _required_env(var: str) -> str:
    value = os.getenv(var)
    if not value:
        raise RuntimeError(f"Environment variable {var} must be set")
    return value


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

    @classmethod
    def from_env(cls) -> "DatabaseConfig":
        """Construct a configuration instance from environment variables."""

        host = _required_env("DATABASE_HOST")
        port = int(os.getenv("DATABASE_PORT", "5432"))
        user = _required_env("DATABASE_USER")
        password = _required_env("DATABASE_PASSWORD")
        database = _required_env("DATABASE_NAME")
        minconn = int(os.getenv("DATABASE_POOL_MIN", "1"))
        maxconn = int(os.getenv("DATABASE_POOL_MAX", "10"))
        return cls(
            host=host,
            port=port,
            user=user,
            password=password,
            database=database,
            minconn=minconn,
            maxconn=maxconn,
        )


class TimescaleDB:
    """Connection pool wrapper for TimescaleDB."""

    def __init__(self, config: DatabaseConfig) -> None:
        self._config = config
        self._pool = SimpleConnectionPool(
            config.minconn,
            config.maxconn,
            host=config.host,
            port=config.port,
            user=config.user,
            password=config.password,
            dbname=config.database,
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
                        id BIGSERIAL PRIMARY KEY,
                        site TEXT NOT NULL,
                        session_id UUID NOT NULL,
                        event_type TEXT NOT NULL,
                        target TEXT NOT NULL,
                        occurred_at TIMESTAMPTZ NOT NULL,
                        meta JSONB NOT NULL,
                        received_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
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
