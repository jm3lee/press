# Copyright (c) Flashoffer Developers
# Released under the MIT license.

from __future__ import annotations

from datetime import date, datetime, timezone
import json
from types import SimpleNamespace
from uuid import uuid4

from psycopg.types.json import Json

from quiz_backend.db import QuizResultsStore


def test_healthcheck(client):
    response = client.get("/health")
    assert response.status_code == 200
    assert response.get_json() == {"status": "ok"}


def _build_payload(
    *,
    passed: bool,
    campaign_id: str | None = None,
    quiz_id: str = "algebra-basics",
) -> dict:
    return {
        "quiz_id": quiz_id,
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


def _build_question_payload(
    *,
    slug: str,
    published_on: date,
    correct_option_id: str = "reminder",
    celebration: str = "classic",
) -> dict:
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
        "celebration": celebration,
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


def test_quiz_stats_endpoint_returns_aggregates(client):
    slug = "algebra-insights"
    client.post("/api/quiz/events", json=_build_payload(passed=True, quiz_id=slug))
    client.post("/api/quiz/events", json=_build_payload(passed=False, quiz_id=slug))
    client.post("/api/quiz/events", json=_build_payload(passed=True, quiz_id=slug))

    response = client.get(f"/api/quiz/stats/{slug}")

    assert response.status_code == 200
    body = response.get_json()
    stats = body["stats"]
    assert stats["quiz_id"] == slug
    assert stats["correct_answers"] == 2
    assert stats["incorrect_answers"] == 1
    assert stats["total_attempts"] == 3
    assert "updated_at" in stats
    assert "created_at" in stats


def test_quiz_stats_endpoint_returns_404_for_missing_slug(client):
    response = client.get("/api/quiz/stats/unknown-slug")

    assert response.status_code == 404
    body = response.get_json()
    assert body["error"] == "quiz_stats_not_found"


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
                    published_on,
                    celebration
                ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
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
                    "classic",
                ),
            )
        conn.commit()

    response = client.get("/api/quiz/today")
    assert response.status_code == 200
    body = response.get_json()
    assert body["question"]["slug"] == "flashoffer-demo"
    assert body["question"]["correct_option_id"] == "reminder"
    assert len(body["question"]["options"]) == 2
    assert body["question"]["celebration"] == "classic"


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
    assert created["celebration"] == payload["celebration"]

    pool: QuizResultsStore = flask_app.config["DB_POOL"]
    with pool.connection() as conn:  # type: ignore[assignment]
        with conn.cursor() as cur:
            cur.execute(
                """
                SELECT slug, correct_option_id, published_on, celebration
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
    assert row[3] == payload["celebration"]


def test_list_quiz_questions_supports_pagination(client):
    older = _build_question_payload(
        slug="alpha-question",
        published_on=date(2024, 7, 1),
        celebration="off",
    )
    newer = _build_question_payload(
        slug="beta-question",
        published_on=date(2024, 8, 1),
        celebration="streamers",
    )

    client.post("/api/quiz/questions", json=older)
    client.post("/api/quiz/questions", json=newer)

    first_page = client.get("/api/quiz/questions", query_string={"limit": "1"})
    assert first_page.status_code == 200
    first_payload = first_page.get_json()
    assert first_payload["pagination"]["count"] == 1
    assert first_payload["questions"][0]["slug"] == "beta-question"
    assert first_payload["questions"][0]["celebration"] == "streamers"

    second_page = client.get(
        "/api/quiz/questions",
        query_string={"limit": "1", "offset": "1"},
    )
    assert second_page.status_code == 200
    second_payload = second_page.get_json()
    assert second_payload["questions"][0]["slug"] == "alpha-question"
    assert second_payload["questions"][0]["celebration"] == "off"


def test_update_quiz_question_overwrites_prompt(client):
    slug = "update-me"
    original = _build_question_payload(slug=slug, published_on=date(2024, 9, 1))
    updated = {
        **original,
        "question": "Updated prompt about conversion levers?",
        "options": [
            {
                "id": "nudge",
                "label": "Send reminder",
                "description": "Keeps audience engaged."
            },
            {
                "id": "delay",
                "label": "Delay outreach",
                "description": "Risk losing momentum."
            }
        ],
        "correct_option_id": "nudge",
        "celebration": "burst",
    }

    client.post("/api/quiz/questions", json=original)

    response = client.put(f"/api/quiz/questions/{slug}", json=updated)
    assert response.status_code == 200
    body = response.get_json()
    assert body["question"]["question"] == updated["question"]
    assert body["question"]["correct_option_id"] == "nudge"
    assert len(body["question"]["options"]) == 2
    assert body["question"]["celebration"] == "burst"


def test_generate_quiz_question_requires_api_key(client, monkeypatch):
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)

    response = client.post(
        "/api/quiz/questions/generate",
        json={"prompt": "Create a finance question."}
    )

    assert response.status_code == 503
    body = response.get_json()
    assert body["error"] == "openai_api_key_missing"


def test_generate_quiz_question_requires_https_base_url(client, monkeypatch):
    monkeypatch.setenv("OPENAI_API_KEY", "unit-test-key")
    monkeypatch.setenv("OPENAI_BASE_URL", "http://insecure-endpoint")

    response = client.post("/api/quiz/questions/generate", json={})

    assert response.status_code == 502
    body = response.get_json()
    assert "openai_client_init_failed" in body["error"]


def test_generate_quiz_question_uses_https_without_proxy(client, monkeypatch):
    monkeypatch.setenv("OPENAI_API_KEY", "unit-test-key")
    monkeypatch.delenv("OPENAI_BASE_URL", raising=False)

    created_http_clients = []

    class DummyHttpClient:
        def __init__(self, *args, **kwargs):
            self.kwargs = kwargs
            self.closed = False
            created_http_clients.append(self)

        def close(self):
            self.closed = True

    monkeypatch.setattr("quiz_backend.app.httpx.Client", DummyHttpClient)

    generated_question = {
        "slug": "draft-slug",
        "question": "What is the call-to-action?",
        "helper_text": None,
        "explanation": None,
        "success_message": None,
        "error_message": None,
        "options": [
            {"id": "cta-a", "label": "Offer discount"},
            {"id": "cta-b", "label": "Send reminder"},
            {"id": "cta-c", "label": "Launch survey"}
        ],
        "correct_option_id": "cta-a",
        "published_on": "2024-01-01",
        "expires_on": None,
        "celebration": "classic",
    }

    class DummyOpenAI:
        calls: list = []

        def __init__(self, *, api_key, base_url, http_client):
            self.api_key = api_key
            self.base_url = base_url
            self.http_client = http_client
            DummyOpenAI.calls.append((base_url, http_client))
            assert base_url.startswith("https://")
            assert isinstance(http_client, DummyHttpClient)
            self.chat = SimpleNamespace(
                completions=SimpleNamespace(
                    create=lambda **kwargs: SimpleNamespace(
                        choices=[
                            SimpleNamespace(
                                message=SimpleNamespace(
                                    content=json.dumps(generated_question)
                                )
                            )
                        ]
                    )
                )
            )

    monkeypatch.setattr("quiz_backend.app.httpx.Client", DummyHttpClient)
    monkeypatch.setattr("quiz_backend.app.OpenAI", DummyOpenAI)

    response = client.post("/api/quiz/questions/generate", json={"prompt": ""})

    assert response.status_code == 200
    body = response.get_json()
    assert body["question"]["slug"] == "draft-slug"
    assert body["question"]["celebration"] == "classic"
    assert body["questions"] == [generated_question]
    assert body["raw_batch"] == [generated_question]
    assert len(DummyOpenAI.calls) == 1
    base_url, used_client = DummyOpenAI.calls[0]
    assert base_url.startswith("https://")
    assert used_client.closed
    assert used_client.kwargs.get("trust_env") is False


def test_generate_quiz_question_rejects_non_string_prompt(client, monkeypatch):
    monkeypatch.setenv("OPENAI_API_KEY", "unit-test-key")

    response = client.post("/api/quiz/questions/generate", json={"prompt": 17})

    assert response.status_code == 400
    body = response.get_json()
    assert body["error"] == "prompt must be a string"


def test_generate_quiz_question_rejects_invalid_count(client, monkeypatch):
    monkeypatch.setenv("OPENAI_API_KEY", "unit-test-key")

    response = client.post(
        "/api/quiz/questions/generate",
        json={"prompt": "", "count": 0},
    )

    assert response.status_code == 400
    body = response.get_json()
    assert "count must be an integer" in body["error"]


def test_generate_quiz_question_batches_requests(client, monkeypatch):
    monkeypatch.setenv("OPENAI_API_KEY", "unit-test-key")

    class DummyHttpClient:
        instances: list["DummyHttpClient"] = []

        def __init__(self, *args, **kwargs):
            self.kwargs = kwargs
            self.closed = False
            DummyHttpClient.instances.append(self)

        def close(self):
            self.closed = True

    class DummyOpenAI:
        def __init__(self, *, api_key, base_url, http_client):
            self.api_key = api_key
            self.base_url = base_url
            self.http_client = http_client
            self._counter = 0
            self.chat = SimpleNamespace(
                completions=SimpleNamespace(create=self._create_completion)
            )

        def _create_completion(self, **_kwargs):
            slug = f"batched-question-{self._counter}"
            self._counter += 1
            payload = {
                "slug": slug,
                "question": f"Question #{self._counter}?",
                "helper_text": None,
                "explanation": None,
                "success_message": None,
                "error_message": None,
                "options": [
                    {"id": "a", "label": "First"},
                    {"id": "b", "label": "Second"},
                    {"id": "c", "label": "Third"},
                ],
                "correct_option_id": "a",
                "published_on": "2024-01-01",
                "expires_on": None,
                "celebration": "off",
            }
            return SimpleNamespace(
                choices=[
                    SimpleNamespace(
                        message=SimpleNamespace(content=json.dumps(payload))
                    )
                ]
            )

    monkeypatch.setattr("quiz_backend.app.httpx.Client", DummyHttpClient)
    monkeypatch.setattr("quiz_backend.app.OpenAI", DummyOpenAI)

    response = client.post(
        "/api/quiz/questions/generate",
        json={"prompt": "", "count": 3},
    )

    assert response.status_code == 200
    body = response.get_json()
    assert len(body["questions"]) == 3
    assert len(body["raw_batch"]) == 3
    assert body["question"]["slug"] == "batched-question-0"


def test_generate_quiz_question_handles_openai_error(client, monkeypatch):
    monkeypatch.setenv("OPENAI_API_KEY", "unit-test-key")

    class DummyHttpClient:
        instances: list["DummyHttpClient"] = []

        def __init__(self, *args, **kwargs):
            self.kwargs = kwargs
            self.closed = False
            DummyHttpClient.instances.append(self)

        def close(self):
            self.closed = True

    class FailingOpenAI:
        def __init__(self, *, api_key, base_url, http_client):  # noqa: D401 - behaviour obvious
            self.api_key = api_key
            self.base_url = base_url
            self.http_client = http_client
            self.chat = SimpleNamespace(
                completions=SimpleNamespace(
                    create=_raise_generation_error,
                )
            )

    def _raise_generation_error(**_kwargs):  # noqa: D401 - helper within test context
        raise RuntimeError("model boom")

    monkeypatch.setattr("quiz_backend.app.httpx.Client", DummyHttpClient)
    monkeypatch.setattr("quiz_backend.app.OpenAI", FailingOpenAI)

    response = client.post(
        "/api/quiz/questions/generate",
        json={"prompt": "Give me a test question."},
    )

    assert response.status_code == 502
    body = response.get_json()
    assert body["error"] == "openai_request_failed: model boom"
    assert DummyHttpClient.instances
    assert DummyHttpClient.instances[0].closed
