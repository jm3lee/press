# Copyright (c) Flashoffer Developers
# Released under the MIT license.

"""Persistence layer for quiz completion events."""

from __future__ import annotations

from datetime import datetime, timezone
from importlib import resources
from typing import Any, Dict

from psycopg2.extras import Json

from backend_common import DatabaseConfig, PostgresPool


def _load_sql(filename: str) -> str:
    """Return the contents of an embedded SQL file."""

    return (
        resources.files(__package__).joinpath("sql", filename).read_text(encoding="utf-8").strip()
    )


CREATE_QUIZ_RESULTS_TABLE_SQL = _load_sql("create_quiz_results_table.sql")

INSERT_QUIZ_RESULT_SQL = _load_sql("insert_quiz_result.sql")


class QuizResultsStore(PostgresPool):
    """Store that manages quiz completion tallies."""

    def initialize(self) -> None:
        with self.connection() as conn:  # type: ignore[assignment]
            with conn.cursor() as cur:
                cur.execute(CREATE_QUIZ_RESULTS_TABLE_SQL)
            conn.commit()

    def record_completion(self, result: Dict[str, Any]) -> Dict[str, Any]:
        occurred_at = _parse_timestamp(result.get("occurred_at"))
        attempts = int(result["attempts"])
        passes = int(result["passes"])
        fails = int(result["fails"])

        row = None
        with self.connection() as conn:  # type: ignore[assignment]
            with conn.cursor() as cur:
                cur.execute(
                    INSERT_QUIZ_RESULT_SQL,
                    (
                        result["quiz_id"],
                        result["user_id"],
                        result.get("attempt_id"),
                        occurred_at,
                        attempts,
                        passes,
                        fails,
                        Json(result.get("payload", {})),
                    ),
                )
                row = cur.fetchone()
            conn.commit()

        if row is None:
            raise RuntimeError("Failed to insert quiz completion record")

        record = {
            "id": row[0],
            "quiz_id": result["quiz_id"],
            "user_id": result["user_id"],
            "attempt_id": result.get("attempt_id"),
            "occurred_at": occurred_at.isoformat(),
            "attempts": attempts,
            "passes": passes,
            "fails": fails,
            "payload": result.get("payload", {}),
            "received_at": _parse_timestamp(row[1]).isoformat() if row else None,
        }
        return record


def _parse_timestamp(value: Any) -> datetime:
    if isinstance(value, datetime):
        if value.tzinfo is None:
            return value.replace(tzinfo=timezone.utc)
        return value.astimezone(timezone.utc)
    if isinstance(value, str):
        cleaned = value.replace("Z", "+00:00")
        parsed = datetime.fromisoformat(cleaned)
        if parsed.tzinfo is None:
            parsed = parsed.replace(tzinfo=timezone.utc)
        return parsed.astimezone(timezone.utc)
    return datetime.now(tz=timezone.utc)


__all__ = ["DatabaseConfig", "QuizResultsStore"]
