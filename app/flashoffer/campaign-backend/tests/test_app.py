from datetime import datetime, timedelta, timezone

from campaign_backend.db import CampaignStore


def test_healthcheck(client):
    response = client.get("/health")
    assert response.status_code == 200
    assert response.get_json() == {"status": "ok"}


def test_time_remaining_returns_payload(client, flask_app):
    pool: CampaignStore = flask_app.config["DB_POOL"]
    ends_at = datetime.now(tz=timezone.utc) + timedelta(minutes=90)

    with pool.connection() as conn:  # type: ignore[assignment]
        with conn.cursor() as cur:
            cur.execute(
                """
                INSERT INTO campaign (id, name, ends_at, quantity_remaining)
                VALUES (%s, %s, %s, %s)
                ON CONFLICT (id) DO UPDATE
                SET ends_at = EXCLUDED.ends_at,
                    quantity_remaining = EXCLUDED.quantity_remaining
                """,
                ("launch", "Launch Countdown", ends_at, 25),
            )
        conn.commit()

    response = client.get(
        "/api/campaign/launch/time_remaining?ct=countdown-timer&cid=launch"
    )
    assert response.status_code == 200
    data = response.get_json()
    assert data["campaign_id"] == "launch"
    assert data["source"] == "countdown-timer"
    assert data["quantity_remaining"] == 25
    assert data["time_remaining_ms"] > 0


def test_missing_campaign_returns_zero(client):
    response = client.get("/api/campaign/unknown/time_remaining")
    assert response.status_code == 404
    data = response.get_json()
    assert data["campaign_id"] == "unknown"
    assert data["time_remaining_ms"] == 0
    assert data["quantity_remaining"] is None
