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


def _build_payload(*, passed: bool) -> dict:
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
    }


def test_quiz_endpoint_requires_bearer_token(flask_app):
    payload = _build_payload(passed=True)

    client = flask_app.test_client()
    response = client.post("/api/events/quiz", json=payload)

    assert response.status_code == 401
    assert "error" in response.get_json()


def test_quiz_endpoint_rejects_invalid_token(flask_app, auth_headers):
    payload = _build_payload(passed=True)

    client = flask_app.test_client()
    response = client.post(
        "/api/events/quiz",
        json=payload,
        headers={
            "Authorization": f"Bearer {auth_headers['Authorization'].split(' ', 1)[1]}--invalid",
        },
    )

    assert response.status_code == 401
    assert "error" in response.get_json()


def test_quiz_completion_is_persisted(client, flask_app):
    payload = _build_payload(passed=True)

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
                SELECT quiz_id, user_id, attempts, passes, fails
                FROM quiz_results
                """
            )
            rows = cur.fetchall()
    assert len(rows) == 1
    assert rows[0][0] == "algebra-basics"
    assert rows[0][2] == 1
    assert rows[0][3] == 1
    assert rows[0][4] == 0


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
