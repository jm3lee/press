"""Database utilities for the analytics backend."""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Dict, Iterable, List, Sequence

from psycopg2.extras import Json, execute_values

from backend_common import DatabaseConfig, PostgresPool


class TimescaleDB(PostgresPool):
    """Connection pool wrapper for TimescaleDB."""

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


__all__ = ["DatabaseConfig", "TimescaleDB"]
