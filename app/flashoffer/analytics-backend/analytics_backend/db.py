# Copyright (c) Flashoffer Developers
# Released under the MIT license.

"""Database utilities for the analytics backend."""

from __future__ import annotations

from datetime import datetime, timezone
from importlib import resources
from typing import Any, Dict, Iterable, List, Sequence

from psycopg.types.json import Json

from backend_common import DatabaseConfig, PostgresPool


def _load_sql(filename: str) -> str:
    """Return the contents of an embedded SQL file."""

    return (
        resources.files(__package__).joinpath("sql", filename).read_text(encoding="utf-8").strip()
    )


CREATE_TIMESCALE_EXTENSION_SQL = _load_sql("create_timescale_extension.sql")

CREATE_ENGAGEMENT_EVENTS_TABLE_SQL = _load_sql("create_engagement_events_table.sql")

CREATE_ENGAGEMENT_EVENTS_HYPERTABLE_SQL = _load_sql(
    "create_engagement_events_hypertable.sql"
)

INSERT_ENGAGEMENT_EVENTS_SQL = _load_sql("insert_engagement_events.sql")

TRUNCATE_ENGAGEMENT_EVENTS_SQL = _load_sql("truncate_engagement_events.sql")

FETCH_RECENT_ENGAGEMENT_EVENTS_SQL = _load_sql(
    "fetch_recent_engagement_events.sql"
)


class TimescaleDB(PostgresPool):
    """Connection pool wrapper for TimescaleDB."""

    def initialize(self) -> None:
        """Ensure the TimescaleDB schema is available."""

        with self.connection() as conn:  # type: ignore[assignment]
            with conn.cursor() as cur:
                cur.execute(CREATE_TIMESCALE_EXTENSION_SQL)
                cur.execute(CREATE_ENGAGEMENT_EVENTS_TABLE_SQL)
                cur.execute(CREATE_ENGAGEMENT_EVENTS_HYPERTABLE_SQL)
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
                _execute_values(cur, INSERT_ENGAGEMENT_EVENTS_SQL, rows)
            conn.commit()
        return len(rows)

    def truncate_events(self) -> None:
        with self.connection() as conn:  # type: ignore[assignment]
            with conn.cursor() as cur:
                cur.execute(TRUNCATE_ENGAGEMENT_EVENTS_SQL)
            conn.commit()

    def fetch_recent_events(self, limit: int = 25) -> List[Dict[str, Any]]:
        limit = max(1, min(limit, 200))
        with self.connection() as conn:  # type: ignore[assignment]
            with conn.cursor() as cur:
                cur.execute(FETCH_RECENT_ENGAGEMENT_EVENTS_SQL, (limit,))
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


def _execute_values(cur: Any, sql: str, rows: Sequence[Sequence[Any]]) -> None:
    """Lightweight replacement for psycopg.extras.execute_values."""

    try:
        prefix, suffix = sql.split("%s", 1)
    except ValueError as exc:  # pragma: no cover - defensive guard
        raise ValueError("Expected a single %s placeholder in SQL template") from exc

    placeholder_segments = []
    flat_params: List[Any] = []
    for row in rows:
        placeholder_segments.append("(" + ", ".join(["%s"] * len(row)) + ")")
        flat_params.extend(row)

    values_clause = ", ".join(placeholder_segments)
    cur.execute(prefix + values_clause + suffix, flat_params)


__all__ = ["DatabaseConfig", "TimescaleDB"]
