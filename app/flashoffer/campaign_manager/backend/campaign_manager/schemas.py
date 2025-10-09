"""Pydantic models used by the campaign manager API."""

from __future__ import annotations

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


class LoginRequest(BaseModel):
    """Credentials submitted when authenticating."""

    username: str = Field(min_length=1)
    password: str = Field(min_length=1)


class LoginResponse(BaseModel):
    """Bearer token returned after a successful login."""

    token: str
    expires_at: datetime


class CampaignPayload(BaseModel):
    """Shared fields for campaign creation and updates."""

    name: Optional[str] = Field(default=None, max_length=200)
    end_time: datetime


class CampaignCreateRequest(CampaignPayload):
    """Request body for creating a new campaign."""

    campaign_id: str = Field(min_length=1)


class CampaignUpdateRequest(CampaignPayload):
    """Request body for updating an existing campaign."""


class CampaignResponse(BaseModel):
    """Envelope returned when listing campaigns."""

    campaign_id: str
    name: Optional[str]
    end_time: datetime
    updated_at: datetime


class CampaignListResponse(BaseModel):
    """Response payload containing multiple campaigns."""

    campaigns: list[CampaignResponse]


__all__ = [
    "CampaignCreateRequest",
    "CampaignListResponse",
    "CampaignPayload",
    "CampaignResponse",
    "CampaignUpdateRequest",
    "LoginRequest",
    "LoginResponse",
]
