# Copyright (c) Flashoffer Developers
# Released under the MIT license.

from datetime import datetime, timedelta, timezone

from campaign_backend.db import CampaignStore


def test_healthcheck(client):
    response = client.get("/health")
    assert response.status_code == 200
    assert response.get_json() == {"status": "ok"}


def test_campaign_endpoint_requires_bearer_token(flask_app):
    client = flask_app.test_client()
    response = client.get("/api/campaign/demo/end_time")

    assert response.status_code == 401
    assert "error" in response.get_json()


def test_campaign_endpoint_rejects_invalid_token(flask_app, auth_headers):
    client = flask_app.test_client()
    response = client.get(
        "/api/campaign/demo/end_time",
        headers={
            "Authorization": f"Bearer {auth_headers['Authorization'].split(' ', 1)[1]}-corrupt",
        },
    )

    assert response.status_code == 401
    assert "error" in response.get_json()


def test_campaign_end_time_returns_remaining_ms(client, flask_app):
    store: CampaignStore = flask_app.config["DB_POOL"]
    deadline = datetime.now(tz=timezone.utc) + timedelta(hours=1, minutes=30)
    store.upsert_campaign("flashoffer-demo", end_time=deadline)

    response = client.get("/api/campaign/flashoffer-demo/end_time")
    assert response.status_code == 200

    payload = response.get_json()
    assert payload["campaign_id"] == "flashoffer-demo"

    returned_deadline = datetime.fromisoformat(
        payload["end_time"].replace("Z", "+00:00")
    )
    assert abs((returned_deadline - deadline).total_seconds()) < 1
    assert 0 <= payload["remaining_ms"] <= 90 * 60 * 1000


def test_missing_campaign_returns_not_found(client):
    response = client.get("/api/campaign/unknown/end_time")
    assert response.status_code == 404
    body = response.get_json()
    assert body["error"] == "campaign not found"


def test_rejects_blank_campaign_identifier(client):
    response = client.get("/api/campaign/%20/end_time")
    assert response.status_code == 400
    assert "campaign id must be provided" in response.get_json()["error"]
