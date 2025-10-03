"""Analytics backend package."""

from __future__ import annotations

from typing import Any

__all__ = ["create_app"]


def __getattr__(name: str) -> Any:
    if name == "create_app":
        from .app import create_app as factory

        return factory
    raise AttributeError(name)
