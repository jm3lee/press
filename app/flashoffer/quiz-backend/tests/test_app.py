# Copyright (c) Flashoffer Developers
# Released under the MIT license.

from __future__ import annotations

from datetime import datetime, timezone
from uuid import uuid4

from quiz_backend.db import QuizResultsStore


def test_healthcheck(client):
    response = client.get("/health")
    assert response.status_code == 200
    assert response.get_json() == {"status": "ok"}


def _build_payload(*, passed: bool, campaign_id: str | None = None) -> dict:
    return {
        "quiz_id": "algebra-basics",
        "user_id": str(uuid4()),
        "event_type": "complete",
        "attempt_id": str(uuid4()),
        "occurred_at": datetime.now(tz=timezone.utc).isoformat(),
        "passed": passed,
        "score": 92 if passed else 54,
        "duration_seconds": 135,
        "metadata": {"source": "pytest"},
        "campaign_id": campaign_id,
    }


def test_quiz_completion_is_persisted(client, flask_app):
    payload = _build_payload(passed=True, campaign_id="launch-2024")

    response = client.post("/api/events/quiz", json=payload)
    assert response.status_code == 201
    body = response.get_json()
    assert body["result"]["passes"] == 1
    assert body["result"]["fails"] == 0
    assert body["result"]["attempts"] == 1

    pool: QuizResultsStore = flask_app.config["DB_POOL"]
    with pool.connection() as conn:  # type: ignore[assignment]
        with conn.cursor() as cur:
            cur.execute(
                """
                SELECT quiz_id, user_id, attempts, passes, fails, campaign_id
                FROM quiz_results
                """
            )
            rows = cur.fetchall()
    assert len(rows) == 1
    assert rows[0][0] == "algebra-basics"
    assert rows[0][2] == 1
    assert rows[0][3] == 1
    assert rows[0][4] == 0
    assert rows[0][5] == "launch-2024"


def test_invalid_event_type_returns_error(client):
    payload = _build_payload(passed=True)
    payload["event_type"] = "start"

    response = client.post("/api/events/quiz", json=payload)
    assert response.status_code == 400
    data = response.get_json()
    assert "Unsupported" in data["error"]


def test_missing_passed_flag_returns_error(client):
    payload = _build_payload(passed=True)
    payload.pop("passed")

    response = client.post("/api/events/quiz", json=payload)
    assert response.status_code == 400
    data = response.get_json()
    assert "passed" in data["error"]


def test_quiz_events_endpoint_returns_recent_results(client):
    first = _build_payload(passed=True, campaign_id="alpha")
    second = _build_payload(passed=False, campaign_id="beta")
    client.post("/api/events/quiz", json=first)
    client.post("/api/events/quiz", json=second)

    response = client.get("/api/events/quiz", query_string={"campaign_id": "alpha", "limit": "5"})

    assert response.status_code == 200
    body = response.get_json()
    assert "results" in body
    assert len(body["results"]) == 1
    result = body["results"][0]
    assert result["campaign_id"] == "alpha"
    assert result["quiz_id"] == "algebra-basics"
    assert result["user_id"]
    assert result["attempts"] == 1
