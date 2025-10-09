# Released under the MIT license.

"""Authentication helpers shared across Flashoffer backend services."""

from __future__ import annotations

import os
import secrets
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Callable, Iterable, Tuple, TYPE_CHECKING

from itsdangerous import BadSignature, BadTimeSignature, URLSafeTimedSerializer

if TYPE_CHECKING:  # pragma: no cover - imported for type checking only
    from flask import Flask, Response


@dataclass(frozen=True)
class BearerAuthConfig:
    """Resolved configuration required to validate campaign manager tokens."""

    username: str
    secret_key: str
    token_ttl_seconds: int


class AuthManager:
    """Manage password verification and token issuance."""

    def __init__(
        self,
        *,
        username: str,
        password_file: Path | None,
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

        if self._password_file is None:
            raise RuntimeError("Admin password file is not configured")

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

        if self._password_file is None:
            raise RuntimeError("Password verification is not configured")

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


def _normalise_env_prefix(service: str | None) -> str | None:
    if service is None:
        return None
    return service.strip().upper().replace("-", "_")


def _resolve_env(
    primary: str | None,
    fallback: str,
    *,
    default: str | None = None,
    required: bool = False,
) -> str:
    candidates = []
    if primary:
        candidates.append(primary)
    candidates.append(fallback)

    for name in candidates:
        value = os.getenv(name)
        if value:
            return value

    if default is not None:
        return default

    if required:
        formatted = " or ".join(candidates)
        raise RuntimeError(f"Missing required environment variable: {formatted}")

    return ""


def load_bearer_auth_config(*, service: str | None = None) -> BearerAuthConfig:
    """Load token validation settings for a backend service."""

    prefix = _normalise_env_prefix(service)

    secret_env = f"{prefix}_SECRET_KEY" if prefix else None
    secret_key = _resolve_env(
        secret_env,
        "CAMPAIGN_MANAGER_SECRET_KEY",
        required=True,
    )

    username_env = f"{prefix}_AUTH_SUBJECT" if prefix else None
    username = _resolve_env(
        username_env,
        "CAMPAIGN_MANAGER_ADMIN_USERNAME",
        default="admin",
    )

    ttl_env = f"{prefix}_TOKEN_TTL_SECONDS" if prefix else None
    ttl_raw = _resolve_env(
        ttl_env,
        "CAMPAIGN_MANAGER_TOKEN_TTL_SECONDS",
        default="28800",
    )
    ttl_seconds = max(int(ttl_raw), 60)

    return BearerAuthConfig(
        username=username,
        secret_key=secret_key,
        token_ttl_seconds=ttl_seconds,
    )


def register_bearer_token_auth(
    app: "Flask",
    auth_manager: AuthManager,
    *,
    exempt_paths: Iterable[str] | None = None,
    failure_handler: Callable[["Response"], "Response"] | None = None,
) -> None:
    """Require a valid bearer token for each request handled by the app."""

    from flask import jsonify, request

    normalised_exempt = {
        _normalise_path(path)
        for path in (exempt_paths or {"/health", "/config"})
    }

    def _reject(message: str) -> "Response":
        response = jsonify({"error": message})
        response.status_code = 401
        if failure_handler is not None:
            response = failure_handler(response)
        return response

    @app.before_request
    def _validate_bearer_token() -> "Response" | None:  # pragma: no cover - Flask hook
        if request.method == "OPTIONS":
            return None

        if _normalise_path(request.path) in normalised_exempt:
            return None

        header = request.headers.get("Authorization", "").strip()
        if not header:
            return _reject("Authorization header missing")

        if not header.lower().startswith("bearer "):
            return _reject("Authorization header must contain a bearer token")

        token = header[7:].strip()
        if not token:
            return _reject("Authorization bearer token is blank")

        try:
            auth_manager.validate_token(token)
        except InvalidTokenError as exc:
            return _reject(str(exc))

        return None


def _normalise_path(path: str) -> str:
    if not path:
        return "/"
    if path == "/":
        return path
    return path.rstrip("/")


__all__ = [
    "AuthManager",
    "BearerAuthConfig",
    "InvalidTokenError",
    "load_bearer_auth_config",
    "register_bearer_token_auth",
]

