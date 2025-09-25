from __future__ import annotations

from datetime import datetime, timezone
from uuid import uuid4

from analytics_backend.db import TimescaleDB


def test_healthcheck(client):
    response = client.get("/health")
    assert response.status_code == 200
    assert response.get_json() == {"status": "ok"}


def test_event_ingest_persists_rows(client, flask_app):
    payload = {
        "site": "press",
        "session_id": str(uuid4()),
        "events": [
            {
                "event_type": "interaction",
                "target": "cta",
                "occurred_at": datetime.now(tz=timezone.utc).isoformat(),
                "meta": {"cta": "subscribe"},
            }
        ],
    }

    response = client.post("/events", json=payload)
    assert response.status_code == 201
    assert response.get_json() == {"inserted": 1}

    pool: TimescaleDB = flask_app.config["DB_POOL"]
    with pool.connection() as conn:  # type: ignore[assignment]
        with conn.cursor() as cur:
            cur.execute("SELECT site, session_id, event_type FROM engagement_events")
            row = cur.fetchone()
    assert row[0] == "press"
    assert row[1] == payload["session_id"]
    assert row[2] == "interaction"
