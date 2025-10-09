# Copyright (c) Flashoffer Developers
# Released under the MIT license.

"""CORS configuration helpers."""

from __future__ import annotations

import os
from typing import Callable, Set

from flask import Flask, Response, request

from pie.logging import logger


def configure_cors(app: Flask, *, component: str) -> Callable[[Response], Response]:
    """Configure permissive CORS support for the given Flask app."""

    cors_logger = logger.bind(component=component, feature="cors")
    cors_allow_origins = os.getenv("CORS_ALLOW_ORIGINS", "")
    cors_logger.info("Loaded CORS_ALLOW_ORIGINS value", value=cors_allow_origins)

    allowed_origins: Set[str] = {
        origin.strip()
        for origin in cors_allow_origins.split(",")
        if origin.strip()
    }
    cors_logger.info(
        "Configured allowed origins",
        allowed_origins=sorted(allowed_origins),
    )

    def apply_cors(response: Response) -> Response:
        if allowed_origins:
            origin = request.headers.get("Origin")
            if origin and ("*" in allowed_origins or origin in allowed_origins):
                response.headers["Access-Control-Allow-Origin"] = origin
                response.headers["Access-Control-Allow-Credentials"] = "true"
                vary = response.headers.get("Vary")
                if vary:
                    vary_values = {value.strip() for value in vary.split(",")}
                    if "Origin" not in vary_values:
                        response.headers["Vary"] = f"{vary}, Origin"
                else:
                    response.headers["Vary"] = "Origin"
            response.headers.setdefault("Access-Control-Allow-Headers", "Content-Type")
            response.headers.setdefault("Access-Control-Allow-Methods", "GET,POST,OPTIONS")
            response.headers.setdefault("Access-Control-Max-Age", "3600")
        return response

    app.after_request(apply_cors)
    return apply_cors


__all__ = ["configure_cors"]
