"""Authentication helpers for the campaign manager API."""

from __future__ import annotations

import os
import secrets
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Tuple

from itsdangerous import BadSignature, BadTimeSignature, URLSafeTimedSerializer


class AuthManager:
    """Manage password verification and token issuance."""

    def __init__(
        self,
        *,
        username: str,
        password_file: Path,
        secret_key: str,
        token_ttl_seconds: int | None = None,
    ) -> None:
        self._username = username
        self._password_file = password_file
        self._secret_key = secret_key
        ttl_env = token_ttl_seconds or int(
            os.getenv("CAMPAIGN_MANAGER_TOKEN_TTL_SECONDS", "28800")
        )
        self._token_ttl = max(ttl_env, 60)
        self._serializer = URLSafeTimedSerializer(secret_key, salt="campaign-manager")
        self._cached_password: str | None = None

    def reload_password(self) -> None:
        """Refresh the cached password from disk."""

        try:
            raw = self._password_file.read_text(encoding="utf-8").strip()
        except FileNotFoundError as exc:  # pragma: no cover - configuration error
            raise RuntimeError(
                "Admin password file is missing; rebuild the container"
            ) from exc

        if not raw:
            raise RuntimeError("Admin password file must not be empty")

        self._cached_password = raw

    def verify_credentials(self, username: str, password: str) -> bool:
        """Return ``True`` when the provided credentials match the admin."""

        if self._cached_password is None:
            self.reload_password()

        assert self._cached_password is not None  # narrow type
        return secrets.compare_digest(username, self._username) and secrets.compare_digest(
            password, self._cached_password
        )

    def issue_token(self) -> Tuple[str, datetime]:
        """Create a bearer token and return it alongside its expiry."""

        expires_at = datetime.now(timezone.utc) + timedelta(seconds=self._token_ttl)
        payload = {"sub": self._username, "exp": expires_at.isoformat()}
        token = self._serializer.dumps(payload)
        return token, expires_at

    def validate_token(self, token: str) -> datetime:
        """Validate the token and return its expiry timestamp."""

        try:
            data = self._serializer.loads(token, max_age=self._token_ttl)
        except (BadSignature, BadTimeSignature) as exc:
            raise InvalidTokenError("Token signature is invalid") from exc

        subject = data.get("sub")
        expiry = data.get("exp")
        if subject != self._username:
            raise InvalidTokenError("Token subject is not recognized")
        if not isinstance(expiry, str):
            raise InvalidTokenError("Token payload is missing an expiry")

        return datetime.fromisoformat(expiry).astimezone(timezone.utc)


class InvalidTokenError(Exception):
    """Raised when a bearer token fails validation."""


__all__ = ["AuthManager", "InvalidTokenError"]
