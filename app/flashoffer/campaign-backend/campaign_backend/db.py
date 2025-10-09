"""Database helpers that power the campaign deadline API."""

from __future__ import annotations

from datetime import datetime, timezone
from importlib import resources
from typing import Any

from backend_common import DatabaseConfig, PostgresPool


def _load_sql(filename: str) -> str:
    """Return the contents of an embedded SQL file."""

    return (
        resources.files(__package__).joinpath("sql", filename).read_text(encoding="utf-8").strip()
    )


CREATE_CAMPAIGN_TABLE_SQL = _load_sql("create_campaign_table.sql")

UPSERT_CAMPAIGN_SQL = _load_sql("upsert_campaign.sql")

FETCH_CAMPAIGN_END_TIME_SQL = _load_sql("fetch_campaign_end_time.sql")


class CampaignStore(PostgresPool):
    """Store that exposes campaign metadata lookups."""

    def initialize(self) -> None:
        """Ensure the campaign table exists."""

        with self.connection() as conn:  # type: ignore[assignment]
            with conn.cursor() as cur:
                cur.execute(CREATE_CAMPAIGN_TABLE_SQL)
            conn.commit()

    def upsert_campaign(self, campaign_id: str, *, end_time: datetime) -> None:
        """Create or update a campaign record."""

        normalized = _ensure_utc(end_time)
        with self.connection() as conn:  # type: ignore[assignment]
            with conn.cursor() as cur:
                cur.execute(UPSERT_CAMPAIGN_SQL, (campaign_id, normalized))
            conn.commit()

    def fetch_end_time(self, campaign_id: str) -> datetime | None:
        """Return the campaign end time or ``None`` when missing."""

        with self.connection() as conn:  # type: ignore[assignment]
            with conn.cursor() as cur:
                cur.execute(FETCH_CAMPAIGN_END_TIME_SQL, (campaign_id,))
                row = cur.fetchone()

        if not row:
            return None

        return _ensure_utc(row[0])


def _ensure_utc(value: Any) -> datetime:
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

    raise TypeError("Campaign timestamps must be datetime or ISO-8601 strings")


__all__ = ["CampaignStore", "DatabaseConfig"]
