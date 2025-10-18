# Copyright (c) Flashoffer Developers
# Released under the MIT license.

from __future__ import annotations

from datetime import date, datetime, timezone
from uuid import uuid4

from psycopg.types.json import Json

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


def _build_question_payload(*, slug: str, published_on: date, correct_option_id: str = "reminder") -> dict:
    return {
        "slug": slug,
        "question": f"Prompt for {slug}?",
        "helper_text": "Think through the conversion funnel.",
        "options": [
            {
                "id": "reminder",
                "label": "Send reminder",
                "description": "Keeps the offer front of mind."
            },
            {
                "id": "survey",
                "label": "Send survey",
                "description": "Collects feedback but slows momentum."
            }
        ],
        "correct_option_id": correct_option_id,
        "published_on": published_on.isoformat(),
        "success_message": "Exactly right.",
        "error_message": "Not quite.",
    }


def test_quiz_completion_is_persisted(client, flask_app):
    payload = _build_payload(passed=True, campaign_id="launch-2024")

    response = client.post("/api/quiz/events", json=payload)
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

    response = client.post("/api/quiz/events", json=payload)
    assert response.status_code == 400
    data = response.get_json()
    assert "Unsupported" in data["error"]


def test_missing_passed_flag_returns_error(client):
    payload = _build_payload(passed=True)
    payload.pop("passed")

    response = client.post("/api/quiz/events", json=payload)
    assert response.status_code == 400
    data = response.get_json()
    assert "passed" in data["error"]


def test_quiz_events_endpoint_returns_recent_results(client):
    first = _build_payload(passed=True, campaign_id="alpha")
    second = _build_payload(passed=False, campaign_id="beta")
    client.post("/api/quiz/events", json=first)
    client.post("/api/quiz/events", json=second)

    response = client.get(
        "/api/quiz/events", query_string={"campaign_id": "alpha", "limit": "5"}
    )

    assert response.status_code == 200
    body = response.get_json()
    assert "results" in body
    assert len(body["results"]) == 1
    result = body["results"][0]
    assert result["campaign_id"] == "alpha"
    assert result["quiz_id"] == "algebra-basics"
    assert result["user_id"]
    assert result["attempts"] == 1


def test_quiz_question_today_returns_active_question(client, flask_app):
    pool: QuizResultsStore = flask_app.config["DB_POOL"]
    options = [
        {
            "id": "reminder",
            "label": "Personalized reminder",
            "description": "Keep the offer top of mind."
        },
        {
            "id": "survey",
            "label": "Follow-up survey",
            "description": "Collects feedback but slows momentum."
        }
    ]
    with pool.connection() as conn:  # type: ignore[assignment]
        with conn.cursor() as cur:
            cur.execute(
                """
                INSERT INTO quiz_questions (
                    slug,
                    question,
                    helper_text,
                    explanation,
                    success_message,
                    error_message,
                    options,
                    correct_option_id,
                    published_on
                ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                """,
                (
                    "flashoffer-demo",
                    "Which follow-up sustains conversion lift?",
                    "Think about friction-free follow-ups.",
                    "Reminders reinforce urgency without blockers.",
                    "Exactly. Reinforce urgency to keep momentum.",
                    "Consider what keeps prospects moving forward.",
                    Json(options),
                    "reminder",
                    date.today(),
                ),
            )
        conn.commit()

    response = client.get("/api/quiz/today")
    assert response.status_code == 200
    body = response.get_json()
    assert body["question"]["slug"] == "flashoffer-demo"
    assert body["question"]["correct_option_id"] == "reminder"
    assert len(body["question"]["options"]) == 2


def test_create_quiz_question_persists_payload(client, flask_app):
    payload = _build_question_payload(slug="new-question", published_on=date.today())

    response = client.post("/api/quiz/questions", json=payload)
    assert response.status_code == 201
    body = response.get_json()
    created = body["question"]
    assert created["slug"] == payload["slug"]
    assert created["correct_option_id"] == payload["correct_option_id"]
    assert created["published_on"] == payload["published_on"]
    assert len(created["options"]) == 2

    pool: QuizResultsStore = flask_app.config["DB_POOL"]
    with pool.connection() as conn:  # type: ignore[assignment]
        with conn.cursor() as cur:
            cur.execute(
                """
                SELECT slug, correct_option_id, published_on
                FROM quiz_questions
                WHERE slug = %s
                """,
                (payload["slug"],),
            )
            row = cur.fetchone()
    assert row is not None
    assert row[0] == payload["slug"]
    assert row[1] == payload["correct_option_id"]
    assert row[2].isoformat() == payload["published_on"]


def test_list_quiz_questions_supports_pagination(client):
    older = _build_question_payload(slug="alpha-question", published_on=date(2024, 7, 1))
    newer = _build_question_payload(slug="beta-question", published_on=date(2024, 8, 1))

    client.post("/api/quiz/questions", json=older)
    client.post("/api/quiz/questions", json=newer)

    first_page = client.get("/api/quiz/questions", query_string={"limit": "1"})
    assert first_page.status_code == 200
    first_payload = first_page.get_json()
    assert first_payload["pagination"]["count"] == 1
    assert first_payload["questions"][0]["slug"] == "beta-question"

    second_page = client.get(
        "/api/quiz/questions",
        query_string={"limit": "1", "offset": "1"},
    )
    assert second_page.status_code == 200
    second_payload = second_page.get_json()
    assert second_payload["questions"][0]["slug"] == "alpha-question"
