"""FastAPI application exposing campaign management endpoints."""

from __future__ import annotations

import os
from pathlib import Path
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

    repository.initialize()
    auth_manager.reload_password()

    app = FastAPI(title="Flashoffer Campaign Manager", version="0.1.0")
    security = HTTPBearer(auto_error=False)

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
