# Copyright (c) Flashoffer Developers
# Released under the MIT license.

"""Tests for the campaign events proxy endpoint."""

from __future__ import annotations

from pathlib import Path

import httpx
import pytest
from fastapi.testclient import TestClient

from campaign_manager.app import create_app
from campaign_manager.auth import InvalidTokenError


class StubRepository:
    """Minimal repository stub used for dependency injection."""

    def initialize(self) -> None:
        pass

    def list_campaigns(self):
        return []

    def fetch_campaign(self, campaign_id: str):
        return None

    def upsert_campaign(self, *, campaign_id: str, name, end_time) -> None:
        pass


class StubAuthManager:
    """Stub auth manager that accepts a fixed token."""

    def __init__(self, token: str = "test-token") -> None:
        self.token = token

    def reload_password(self) -> None:
        pass

    def validate_token(self, token: str) -> None:
        if token != self.token:
            raise InvalidTokenError("Invalid token")

    def verify_credentials(self, username: str, password: str) -> bool:
        return True

    def issue_token(self) -> tuple[str, str]:
        return (self.token, "2099-01-01T00:00:00Z")


@pytest.fixture
def configured_app(monkeypatch: pytest.MonkeyPatch, tmp_path: Path):
    """Configure the FastAPI app with stub dependencies for testing."""

    repository = StubRepository()
    auth_manager = StubAuthManager()

    monkeypatch.setattr("campaign_manager.app._create_repository", lambda: repository)
    monkeypatch.setattr("campaign_manager.app._create_auth_manager", lambda: auth_manager)
    monkeypatch.setenv("CAMPAIGN_MANAGER_ANALYTICS_RECENT_URL", "http://analytics.test/events/recent")
    monkeypatch.setenv(
        "CAMPAIGN_MANAGER_QUIZ_RECENT_URL", "http://quiz.test/api/quiz/events"
    )
    monkeypatch.setenv("CAMPAIGN_MANAGER_STATIC_DIR", str(tmp_path))

    app = create_app()
    return app, auth_manager


def _authorized_headers(token: str) -> dict[str, str]:
    return {"Authorization": f"Bearer {token}"}


def test_campaign_events_successfully_proxies_response(configured_app):
    app, auth_manager = configured_app

    async def fake_get(url: str, params=None, headers=None):
        assert params == {"campaign_id": "launch", "limit": "200"}
        request = httpx.Request("GET", url, params=params)
        if url == "http://analytics.test/events/recent":
            payload = {
                "events": [
                    {
                        "id": "eng-1",
                        "event_type": "cta_click",
                        "target": "hero",
                        "occurred_at": "2024-04-01T12:00:00Z",
                        "received_at": "2024-04-01T12:00:01Z",
                        "site": "press",
                        "session_id": "sess-1",
                        "meta": {"cta": "hero"},
                    }
                ]
            }
            return httpx.Response(status_code=200, json=payload, request=request)
        if url == "http://quiz.test/api/quiz/events":
            payload = {
                "results": [
                    {
                        "id": 42,
                        "quiz_id": "knowledge-check",
                        "user_id": "user-7",
                        "attempt_id": "attempt-9",
                        "campaign_id": "launch",
                        "occurred_at": "2024-04-01T11:59:59Z",
                        "received_at": "2024-04-01T12:00:00Z",
                        "attempts": 1,
                        "passes": 1,
                        "fails": 0,
                        "payload": {"score": 100},
                    }
                ]
            }
            return httpx.Response(status_code=200, json=payload, request=request)
        raise AssertionError(f"Unexpected URL {url}")

    app.state.analytics_client.get = fake_get  # type: ignore[assignment]

    with TestClient(app) as client:
        response = client.get(
            "/api/campaigns/launch/events?limit=500",
            headers=_authorized_headers(auth_manager.token),
        )

    assert response.status_code == 200
    data = response.json()
    assert len(data["events"]) == 2
    assert data["events"][0]["id"] == "eng-1"
    quiz_event = next(event for event in data["events"] if event["event_type"] == "quiz-complete")
    assert quiz_event["id"] == "quiz-42"
    assert quiz_event["target"] == "knowledge-check"
    assert quiz_event["session_id"] == "user-7"
    assert quiz_event["meta"]["campaign_id"] == "launch"
    assert quiz_event["meta"]["payload"] == {"score": 100}


def test_campaign_events_returns_bad_gateway_on_error_status(configured_app):
    app, auth_manager = configured_app

    async def fake_get(url: str, params=None, headers=None):
        request = httpx.Request("GET", url, params=params)
        if url == "http://analytics.test/events/recent":
            return httpx.Response(status_code=503, request=request)
        return httpx.Response(
            status_code=200,
            json={"results": []},
            request=request,
        )

    app.state.analytics_client.get = fake_get  # type: ignore[assignment]

    with TestClient(app) as client:
        response = client.get(
            "/api/campaigns/spring-sale/events",
            headers=_authorized_headers(auth_manager.token),
        )

    assert response.status_code == 502
    assert "503" in response.json()["detail"]


def test_campaign_events_handles_request_exceptions(configured_app):
    app, auth_manager = configured_app

    async def fake_get(url: str, params=None, headers=None):
        request = httpx.Request("GET", url, params=params)
        raise httpx.ConnectError("boom", request=request)

    app.state.analytics_client.get = fake_get  # type: ignore[assignment]

    with TestClient(app) as client:
        response = client.get(
            "/api/campaigns/summer/events",
            headers=_authorized_headers(auth_manager.token),
        )

    assert response.status_code == 502
    assert "analytics services" in response.json()["detail"]


def test_campaign_events_rejects_non_object_payloads(configured_app):
    app, auth_manager = configured_app

    async def fake_get(url: str, params=None, headers=None):
        request = httpx.Request("GET", url, params=params)
        if url == "http://analytics.test/events/recent":
            return httpx.Response(status_code=200, json={"events": []}, request=request)
        return httpx.Response(status_code=200, content=b"[]", request=request)

    app.state.analytics_client.get = fake_get  # type: ignore[assignment]

    with TestClient(app) as client:
        response = client.get(
            "/api/campaigns/autumn/events",
            headers=_authorized_headers(auth_manager.token),
        )

    assert response.status_code == 502
    assert "JSON object" in response.json()["detail"]
