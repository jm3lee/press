from __future__ import annotations

"""Data model for metadata schema versioning."""

from dataclasses import dataclass

DEFAULT_SCHEMA = "v1"

__all__ = ["Schema", "DEFAULT_SCHEMA"]


@dataclass
class Schema:
    """Metadata schema information."""

    schema: str = DEFAULT_SCHEMA
