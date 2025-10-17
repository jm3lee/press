# Copyright (c) Flashoffer Developers
# Released under the MIT license.

"""Persistence layer for quiz completion events and metadata."""

from __future__ import annotations

from datetime import date, datetime, timezone
from importlib import resources
from typing import Any, Dict, List, Optional

from psycopg.types.json import Json

from backend_common import DatabaseConfig, PostgresPool


def _load_sql(filename: str) -> str:
    """Return the contents of an embedded SQL file."""

    return (
        resources.files(__package__).joinpath("sql", filename).read_text(encoding="utf-8").strip()
    )


CREATE_QUIZ_RESULTS_TABLE_SQL = _load_sql("create_quiz_results_table.sql")

INSERT_QUIZ_RESULT_SQL = _load_sql("insert_quiz_result.sql")

FETCH_RECENT_QUIZ_RESULTS_SQL = _load_sql("fetch_recent_quiz_results.sql")

ENSURE_CAMPAIGN_ID_COLUMN_SQL = _load_sql("ensure_campaign_id_column.sql")

CREATE_QUIZ_QUESTIONS_TABLE_SQL = _load_sql("create_quiz_questions_table.sql")

FETCH_QUESTION_OF_DAY_SQL = _load_sql("fetch_question_of_day.sql")

ENSURE_QUIZ_QUESTIONS_INDEX_SQL = _load_sql("ensure_quiz_questions_index.sql")


class QuizResultsStore(PostgresPool):
    """Store that manages quiz completion tallies."""

    def initialize(self) -> None:
        with self.connection() as conn:  # type: ignore[assignment]
            with conn.cursor() as cur:
                cur.execute(CREATE_QUIZ_RESULTS_TABLE_SQL)
                cur.execute(ENSURE_CAMPAIGN_ID_COLUMN_SQL)
                cur.execute(CREATE_QUIZ_QUESTIONS_TABLE_SQL)
                cur.execute(ENSURE_QUIZ_QUESTIONS_INDEX_SQL)
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
                        result.get("campaign_id"),
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
            "campaign_id": result.get("campaign_id"),
            "occurred_at": occurred_at.isoformat(),
            "attempts": attempts,
            "passes": passes,
            "fails": fails,
            "payload": result.get("payload", {}),
            "received_at": _parse_timestamp(row[1]).isoformat() if row else None,
        }
        return record

    def fetch_recent_results(
        self,
        *,
        limit: int = 25,
        campaign_id: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        normalized_limit = max(1, min(limit, 200))
        with self.connection() as conn:  # type: ignore[assignment]
            with conn.cursor() as cur:
                cur.execute(
                    FETCH_RECENT_QUIZ_RESULTS_SQL,
                    (campaign_id, campaign_id, normalized_limit),
                )
                rows = cur.fetchall()

        results: List[Dict[str, Any]] = []
        for row in rows:
            results.append(
                {
                    "id": row[0],
                    "quiz_id": row[1],
                    "user_id": row[2],
                    "attempt_id": row[3],
                    "campaign_id": row[4],
                    "occurred_at": _parse_timestamp(row[5]).isoformat(),
                    "attempts": int(row[6]),
                    "passes": int(row[7]),
                    "fails": int(row[8]),
                    "payload": row[9] or {},
                    "received_at": _parse_timestamp(row[10]).isoformat(),
                }
            )

        return results

    def fetch_question_of_day(
        self,
        *,
        today: Optional[date] = None,
    ) -> Optional[Dict[str, Any]]:
        target_date = today or datetime.now(tz=timezone.utc).date()

        row = None
        with self.connection() as conn:  # type: ignore[assignment]
            with conn.cursor() as cur:
                cur.execute(
                    FETCH_QUESTION_OF_DAY_SQL,
                    (
                        target_date,
                        target_date,
                    ),
                )
                row = cur.fetchone()

        if row is None:
            return None

        (
            question_id,
            slug,
            question,
            helper_text,
            explanation,
            success_message,
            error_message,
            options,
            correct_option_id,
            published_on,
            expires_on,
        ) = row

        normalized_options: List[Dict[str, Any]] = []
        if isinstance(options, (list, tuple)):
            for option in options:
                if isinstance(option, dict):
                    normalized_options.append(option)

        return {
            "id": question_id,
            "slug": slug,
            "question": question,
            "helper_text": helper_text,
            "explanation": explanation,
            "success_message": success_message,
            "error_message": error_message,
            "options": normalized_options,
            "correct_option_id": correct_option_id,
            "published_on": (
                published_on.isoformat()
                if hasattr(published_on, "isoformat")
                else str(published_on)
            ),
            "expires_on": (
                expires_on.isoformat()
                if hasattr(expires_on, "isoformat") and expires_on is not None
                else None
            ),
        }


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
