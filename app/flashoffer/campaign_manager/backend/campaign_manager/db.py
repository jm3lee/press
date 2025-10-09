# Copyright (c) Flashoffer Developers
# Released under the MIT license.

"""Database helpers for the campaign manager API."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from typing import List, Optional

from backend_common import DatabaseConfig, PostgresPool


@dataclass
class CampaignRecord:
    """Structured campaign metadata fetched from PostgreSQL."""

    campaign_id: str
    name: Optional[str]
    end_time: datetime
    updated_at: datetime


class CampaignRepository(PostgresPool):
    """Expose CRUD helpers for campaign records."""

    def initialize(self) -> None:
        """Ensure the campaign table exists with the expected columns."""

        with self.connection() as conn:  # type: ignore[assignment]
            with conn.cursor() as cur:
                cur.execute(
                    """
                    CREATE TABLE IF NOT EXISTS campaign (
                        id TEXT PRIMARY KEY,
                        name TEXT,
                        end_time TIMESTAMPTZ NOT NULL,
                        updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
                    )
                    """
                )
            conn.commit()

    def list_campaigns(self) -> List[CampaignRecord]:
        """Return all campaign records ordered alphabetically by id."""

        with self.connection() as conn:  # type: ignore[assignment]
            with conn.cursor() as cur:
                cur.execute(
                    """
                    SELECT id, name, end_time, updated_at
                    FROM campaign
                    ORDER BY id ASC
                    """
                )
                rows = cur.fetchall()

        return [
            CampaignRecord(
                campaign_id=row[0],
                name=row[1],
                end_time=_ensure_utc(row[2]),
                updated_at=_ensure_utc(row[3]),
            )
            for row in rows
        ]

    def upsert_campaign(
        self,
        *,
        campaign_id: str,
        name: Optional[str],
        end_time: datetime,
    ) -> None:
        """Create or update a campaign record with the provided metadata."""

        normalized_end = _ensure_utc(end_time)

        with self.connection() as conn:  # type: ignore[assignment]
            with conn.cursor() as cur:
                cur.execute(
                    """
                    INSERT INTO campaign (id, name, end_time)
                    VALUES (%s, %s, %s)
                    ON CONFLICT (id)
                    DO UPDATE SET name = EXCLUDED.name,
                        end_time = EXCLUDED.end_time,
                        updated_at = NOW()
                    """,
                    (campaign_id, name, normalized_end),
                )
            conn.commit()


    def fetch_campaign(self, campaign_id: str) -> CampaignRecord | None:
        """Return a single campaign record when available."""

        with self.connection() as conn:  # type: ignore[assignment]
            with conn.cursor() as cur:
                cur.execute(
                    "SELECT id, name, end_time, updated_at FROM campaign WHERE id = %s",
                    (campaign_id,),
                )
                row = cur.fetchone()

        if not row:
            return None

        return CampaignRecord(
            campaign_id=row[0],
            name=row[1],
            end_time=_ensure_utc(row[2]),
            updated_at=_ensure_utc(row[3]),
        )

def _ensure_utc(value: datetime | str) -> datetime:
    """Normalize aware timestamps and ISO strings to UTC-aware datetimes."""

    if isinstance(value, datetime):
        if value.tzinfo is None:
            return value.replace(tzinfo=timezone.utc)
        return value.astimezone(timezone.utc)

    cleaned = value.replace("Z", "+00:00")
    parsed = datetime.fromisoformat(cleaned)
    if parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=timezone.utc)
    return parsed.astimezone(timezone.utc)


__all__ = ["CampaignRecord", "CampaignRepository", "DatabaseConfig"]
