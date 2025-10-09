# Copyright (c) Flashoffer Developers
# Released under the MIT license.

"""FastAPI application exposing campaign management endpoints."""

from __future__ import annotations

import os
from pathlib import Path
from typing import Any, Dict

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

    repository.initialize()
    auth_manager.reload_password()

    app = FastAPI(title="Flashoffer Campaign Manager", version="0.1.0")
    security = HTTPBearer(auto_error=False)

    analytics_client = httpx.AsyncClient(
        timeout=httpx.Timeout(10.0, connect=5.0),
        headers={"Accept": "application/json"},
    )
    app.state.analytics_recent_url = analytics_url
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

        params = {"campaign_id": normalized_id}
        if limit is not None:
            sanitized = max(1, min(limit, 200))
            params["limit"] = str(sanitized)

        client: httpx.AsyncClient = app.state.analytics_client
        analytics_recent_url: str = app.state.analytics_recent_url

        try:
            response = await client.get(analytics_recent_url, params=params)
        except httpx.RequestError as exc:
            raise HTTPException(
                status_code=status.HTTP_502_BAD_GATEWAY,
                detail=f"Failed to contact analytics backend: {exc}",
            ) from exc

        if response.status_code >= 400:
            raise HTTPException(
                status_code=status.HTTP_502_BAD_GATEWAY,
                detail=(
                    "Analytics backend returned unexpected status "
                    f"{response.status_code}"
                ),
            )

        try:
            payload = response.json()
        except ValueError as exc:
            raise HTTPException(
                status_code=status.HTTP_502_BAD_GATEWAY,
                detail="Analytics backend response was not valid JSON",
            ) from exc

        if not isinstance(payload, dict):
            raise HTTPException(
                status_code=status.HTTP_502_BAD_GATEWAY,
                detail="Analytics backend response must be a JSON object",
            )

        return payload

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


def _normalize_name(name: str | None) -> str | None:
    if name is None:
        return None
    stripped = name.strip()
    return stripped or None


__all__ = ["create_app"]
