# Copyright (c) Flashoffer Developers
# Released under the MIT license.

"""FastAPI application exposing campaign management endpoints."""

from __future__ import annotations

import asyncio
import os
from pathlib import Path
from typing import Any, Dict, List

import httpx
from fastapi import Depends, FastAPI, HTTPException, status
from fastapi.responses import FileResponse
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from fastapi.staticfiles import StaticFiles

from backend_common import DatabaseConfig

from .auth import AuthManager, InvalidTokenError
from .db import CampaignRecord, CampaignRepository
from .schemas import (
    CampaignCreateRequest,
    CampaignListResponse,
    CampaignResponse,
    CampaignUpdateRequest,
    LoginRequest,
    LoginResponse,
)


def _load_secret() -> str:
    secret = os.getenv("CAMPAIGN_MANAGER_SECRET_KEY")
    if not secret:
        raise RuntimeError("CAMPAIGN_MANAGER_SECRET_KEY must be set")
    return secret


def _password_path() -> Path:
    raw_path = os.getenv("CAMPAIGN_MANAGER_ADMIN_PASSWORD_FILE")
    if not raw_path:
        raise RuntimeError("CAMPAIGN_MANAGER_ADMIN_PASSWORD_FILE must be set")
    return Path(raw_path)


def _static_dir() -> Path:
    raw_path = os.getenv("CAMPAIGN_MANAGER_STATIC_DIR", "/app/static")
    return Path(raw_path)


def _analytics_recent_url() -> str:
    raw_recent = os.getenv("CAMPAIGN_MANAGER_ANALYTICS_RECENT_URL", "").strip()
    if raw_recent:
        return raw_recent

    raw_base = os.getenv("CAMPAIGN_MANAGER_ANALYTICS_BASE", "http://analytics-backend:8000").strip()
    if not raw_base:
        raise RuntimeError(
            "CAMPAIGN_MANAGER_ANALYTICS_BASE must be configured with a valid URL",
        )
    base = raw_base.rstrip("/")
    return f"{base}/events/recent"


def _quiz_recent_url() -> str:
    raw_recent = os.getenv("CAMPAIGN_MANAGER_QUIZ_RECENT_URL", "").strip()
    if raw_recent:
        return raw_recent

    raw_base = os.getenv("CAMPAIGN_MANAGER_QUIZ_BASE", "http://quiz-backend:8000").strip()
    if not raw_base:
        raise RuntimeError(
            "CAMPAIGN_MANAGER_QUIZ_BASE must be configured with a valid URL",
        )
    base = raw_base.rstrip("/")
    return f"{base}/api/events/quiz"


def _create_auth_manager() -> AuthManager:
    username = os.getenv("CAMPAIGN_MANAGER_ADMIN_USERNAME", "admin")
    return AuthManager(
        username=username,
        password_file=_password_path(),
        secret_key=_load_secret(),
    )


def _create_repository() -> CampaignRepository:
    config = DatabaseConfig.from_env()
    return CampaignRepository(config)


def _as_response(record: CampaignRecord) -> CampaignResponse:
    return CampaignResponse(
        campaign_id=record.campaign_id,
        name=record.name,
        end_time=record.end_time,
        updated_at=record.updated_at,
    )


def create_app() -> FastAPI:
    """Instantiate and configure the FastAPI application."""

    repository = _create_repository()
    auth_manager = _create_auth_manager()
    analytics_url = _analytics_recent_url()
    quiz_url = _quiz_recent_url()

    repository.initialize()
    auth_manager.reload_password()

    app = FastAPI(title="Flashoffer Campaign Manager", version="0.1.0")
    security = HTTPBearer(auto_error=False)

    analytics_client = httpx.AsyncClient(
        timeout=httpx.Timeout(10.0, connect=5.0),
        headers={"Accept": "application/json"},
    )
    app.state.analytics_recent_url = analytics_url
    app.state.quiz_recent_url = quiz_url
    app.state.analytics_client = analytics_client

    @app.on_event("shutdown")
    async def _close_analytics_client() -> None:  # pragma: no cover - FastAPI handles lifecycle
        await analytics_client.aclose()

    static_dir = _static_dir()
    assets_dir = static_dir / "assets"
    if assets_dir.exists():
        app.mount("/assets", StaticFiles(directory=assets_dir), name="assets")

    def _require_token(
        credentials: HTTPAuthorizationCredentials | None = Depends(security),
    ) -> str:
        if credentials is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Authorization header missing",
            )

        try:
            auth_manager.validate_token(credentials.credentials)
        except InvalidTokenError as exc:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=str(exc),
            ) from exc

        return credentials.credentials

    @app.post("/api/auth/login", response_model=LoginResponse)
    def login(payload: LoginRequest) -> LoginResponse:
        """Authenticate a user and return a bearer token."""

        username = payload.username.strip()
        password = payload.password
        if not auth_manager.verify_credentials(username, password):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid username or password",
            )

        token, expires = auth_manager.issue_token()
        return LoginResponse(token=token, expires_at=expires)

    @app.get("/api/campaigns", response_model=CampaignListResponse)
    def list_campaigns(_: str = Depends(_require_token)) -> CampaignListResponse:
        """Return all campaigns available in the database."""

        records = repository.list_campaigns()
        return CampaignListResponse(campaigns=[_as_response(record) for record in records])

    @app.post("/api/campaigns", response_model=CampaignResponse)
    def create_campaign(
        request: CampaignCreateRequest,
        _: str = Depends(_require_token),
    ) -> CampaignResponse:
        """Create a new campaign record."""

        campaign_id = request.campaign_id.strip()
        if not campaign_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Campaign identifier must not be blank",
            )

        repository.upsert_campaign(
            campaign_id=campaign_id,
            name=_normalize_name(request.name),
            end_time=request.end_time,
        )
        record = repository.fetch_campaign(campaign_id)
        if record is None:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to persist campaign",
            )
        return _as_response(record)

    @app.put("/api/campaigns/{campaign_id}", response_model=CampaignResponse)
    def update_campaign(
        campaign_id: str,
        request: CampaignUpdateRequest,
        _: str = Depends(_require_token),
    ) -> CampaignResponse:
        """Update an existing campaign with new metadata."""

        normalized_id = campaign_id.strip()
        if not normalized_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Campaign identifier must not be blank",
            )

        repository.upsert_campaign(
            campaign_id=normalized_id,
            name=_normalize_name(request.name),
            end_time=request.end_time,
        )
        record = repository.fetch_campaign(normalized_id)
        if record is None:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to load updated campaign",
            )
        return _as_response(record)

    @app.get("/api/campaigns/{campaign_id}/events")
    async def campaign_events(
        campaign_id: str,
        limit: int | None = None,
        _: str = Depends(_require_token),
    ) -> Dict[str, Any]:
        """Proxy recent engagement events from the analytics backend."""

        normalized_id = campaign_id.strip()
        if not normalized_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Campaign identifier must not be blank",
            )

        sanitized = 25
        if limit is not None:
            sanitized = max(1, min(limit, 200))

        params = {"campaign_id": normalized_id, "limit": str(sanitized)}

        client: httpx.AsyncClient = app.state.analytics_client
        analytics_recent_url: str = app.state.analytics_recent_url
        quiz_recent_url: str = app.state.quiz_recent_url

        try:
            analytics_response, quiz_response = await asyncio.gather(
                client.get(analytics_recent_url, params=params.copy()),
                client.get(quiz_recent_url, params=params.copy()),
            )
        except httpx.RequestError as exc:
            raise HTTPException(
                status_code=status.HTTP_502_BAD_GATEWAY,
                detail=f"Failed to contact analytics services: {exc}",
            ) from exc

        for backend, response in (
            ("Analytics", analytics_response),
            ("Quiz", quiz_response),
        ):
            if response.status_code >= 400:
                raise HTTPException(
                    status_code=status.HTTP_502_BAD_GATEWAY,
                    detail=f"{backend} backend returned unexpected status {response.status_code}",
                )

        try:
            analytics_payload = analytics_response.json()
        except ValueError as exc:
            raise HTTPException(
                status_code=status.HTTP_502_BAD_GATEWAY,
                detail="Analytics backend response was not valid JSON",
            ) from exc

        try:
            quiz_payload = quiz_response.json()
        except ValueError as exc:
            raise HTTPException(
                status_code=status.HTTP_502_BAD_GATEWAY,
                detail="Quiz backend response was not valid JSON",
            ) from exc

        if not isinstance(analytics_payload, dict):
            raise HTTPException(
                status_code=status.HTTP_502_BAD_GATEWAY,
                detail="Analytics backend response must be a JSON object",
            )
        if not isinstance(quiz_payload, dict):
            raise HTTPException(
                status_code=status.HTTP_502_BAD_GATEWAY,
                detail="Quiz backend response must be a JSON object",
            )

        engagement_events: List[Dict[str, Any]] = []
        raw_events = analytics_payload.get("events")
        if isinstance(raw_events, list):
            engagement_events = [event for event in raw_events if isinstance(event, dict)]

        quiz_results: List[Dict[str, Any]] = []
        raw_quiz_results = quiz_payload.get("results")
        if isinstance(raw_quiz_results, list):
            quiz_results = [result for result in raw_quiz_results if isinstance(result, dict)]

        combined: List[Dict[str, Any]] = []
        combined.extend(engagement_events)
        combined.extend(_convert_quiz_result(result) for result in quiz_results)
        combined.sort(key=_event_sort_key, reverse=True)

        return {"events": combined[:sanitized]}

    index_path = static_dir / "index.html"

    @app.get("/", include_in_schema=False)
    def serve_index() -> FileResponse:
        if not index_path.exists():
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="UI missing")
        return FileResponse(index_path)

    @app.get("/{full_path:path}", include_in_schema=False)
    def serve_spa(full_path: str) -> FileResponse:
        if not index_path.exists():
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="UI missing")
        return FileResponse(index_path)

    return app


def _convert_quiz_result(result: Dict[str, Any]) -> Dict[str, Any]:
    """Convert quiz completion records into the console event schema."""

    payload = result.get("payload") or {}
    meta: Dict[str, Any] = {
        "quiz_id": result.get("quiz_id"),
        "user_id": result.get("user_id"),
        "attempt_id": result.get("attempt_id"),
        "campaign_id": result.get("campaign_id"),
        "attempts": result.get("attempts"),
        "passes": result.get("passes"),
        "fails": result.get("fails"),
        "payload": payload,
    }
    cleaned_meta = {key: value for key, value in meta.items() if value is not None or key == "payload"}

    occurred_at = result.get("occurred_at")
    received_at = result.get("received_at") or occurred_at

    return {
        "id": f"quiz-{result.get('id')}",
        "event_type": "quiz-complete",
        "target": result.get("quiz_id") or "quiz",
        "occurred_at": occurred_at,
        "received_at": received_at,
        "site": "quiz-service",
        "session_id": result.get("user_id") or "unknown-user",
        "meta": cleaned_meta,
    }


def _event_sort_key(event: Dict[str, Any]) -> str:
    """Return the timestamp used when ordering mixed event streams."""

    received_at = event.get("received_at")
    occurred_at = event.get("occurred_at")
    if isinstance(received_at, str):
        return received_at
    if isinstance(occurred_at, str):
        return occurred_at
    return ""


def _normalize_name(name: str | None) -> str | None:
    if name is None:
        return None
    stripped = name.strip()
    return stripped or None


__all__ = ["create_app"]
