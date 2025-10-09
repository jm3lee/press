from __future__ import annotations

from datetime import datetime, timezone
from uuid import uuid4

from analytics_backend.db import TimescaleDB


def test_healthcheck(client):
    response = client.get("/health")
    assert response.status_code == 200
    assert response.get_json() == {"status": "ok"}


def _build_event(event_type: str, target: str) -> dict:
    return {
        "type": event_type,
        "target": target,
        "at": datetime.now(tz=timezone.utc).isoformat(),
        "meta": {"source": "pytest"},
    }


def test_event_ingest_persists_rows(client, flask_app):
    payload = {
        "site": "press",
        "session_id": str(uuid4()),
        "events": [
            _build_event("interaction", "cta"),
            _build_event("view", "hero"),
        ],
    }

    response = client.post("/events", json=payload)
    assert response.status_code == 201
    assert response.get_json() == {"inserted": 2}

    pool: TimescaleDB = flask_app.config["DB_POOL"]
    with pool.connection() as conn:  # type: ignore[assignment]
        with conn.cursor() as cur:
            cur.execute(
                "SELECT site, session_id, event_type, target FROM engagement_events"
            )
            rows = cur.fetchall()
    assert {row[2] for row in rows} == {"interaction", "view"}
    assert {row[3] for row in rows} == {"cta", "hero"}
    assert all(row[0] == "press" for row in rows)
    assert all(row[1] == payload["session_id"] for row in rows)


def test_recent_events_endpoint_returns_payload(client, flask_app):
    payload = {
        "site": "press",
        "session_id": str(uuid4()),
        "events": [_build_event("scroll-depth", "page")],
    }
    post_response = client.post("/events", json=payload)
    assert post_response.status_code == 201

    response = client.get("/events/recent?limit=5")
    assert response.status_code == 200
    data = response.get_json()
    assert "events" in data
    assert len(data["events"]) >= 1
    latest = data["events"][0]
    assert latest["event_type"] == "scroll-depth"
    assert latest["target"] == "page"
    assert latest["site"] == "press"
    assert latest["session_id"] == payload["session_id"]
    assert "occurred_at" in latest
    assert "received_at" in latest
    assert isinstance(latest["meta"], dict)
