"""Database utilities for campaign countdown metadata."""

from __future__ import annotations

from datetime import datetime, timedelta, timezone
from typing import Any, Dict, Optional

from backend_common import DatabaseConfig, PostgresPool


class CampaignStore(PostgresPool):
    """Store providing access to campaign countdown information."""

    def initialize(self) -> None:
        """Create the campaign table if it is missing."""

        with self.connection() as conn:  # type: ignore[assignment]
            with conn.cursor() as cur:
                cur.execute(
                    """
                    CREATE TABLE IF NOT EXISTS campaign (
                        id TEXT PRIMARY KEY,
                        name TEXT NOT NULL,
                        ends_at TIMESTAMPTZ NOT NULL,
                        quantity_remaining INTEGER,
                        updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
                    )
                    """
                )
            conn.commit()

    def fetch_time_remaining(self, campaign_id: str) -> Optional[Dict[str, Any]]:
        """Return the remaining time details for a campaign."""

        with self.connection() as conn:  # type: ignore[assignment]
            with conn.cursor() as cur:
                cur.execute(
                    """
                    SELECT ends_at, quantity_remaining
                    FROM campaign
                    WHERE id = %s
                    """,
                    (campaign_id,),
                )
                row = cur.fetchone()

        if row is None:
            return None

        ends_at = _normalise_timestamp(row[0])
        remaining = max(
            int((ends_at - datetime.now(tz=timezone.utc)).total_seconds() * 1000),
            0,
        )
        quantity = row[1] if row[1] is not None else None

        return {
            "campaign_id": campaign_id,
            "time_remaining_ms": remaining,
            "quantity_remaining": quantity,
            "ends_at": ends_at,
        }

    def ensure_demo_campaign(self) -> None:
        """Seed the demo campaign when no record exists."""

        with self.connection() as conn:  # type: ignore[assignment]
            with conn.cursor() as cur:
                cur.execute(
                    "SELECT 1 FROM campaign WHERE id = %s",
                    ("flashoffer-demo",),
                )
                exists = cur.fetchone() is not None
                if not exists:
                    cur.execute(
                        """
                        INSERT INTO campaign (id, name, ends_at, quantity_remaining)
                        VALUES (%s, %s, %s, %s)
                        ON CONFLICT (id) DO NOTHING
                        """,
                        (
                            "flashoffer-demo",
                            "Flashoffer Demo",
                            datetime.now(tz=timezone.utc) + timedelta(hours=46),
                            128,
                        ),
                    )
            conn.commit()

    def truncate(self) -> None:
        """Remove campaign records, useful for tests."""

        with self.connection() as conn:  # type: ignore[assignment]
            with conn.cursor() as cur:
                cur.execute("TRUNCATE campaign")
            conn.commit()


def _normalise_timestamp(value: Any) -> datetime:
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


__all__ = ["CampaignStore", "DatabaseConfig"]
