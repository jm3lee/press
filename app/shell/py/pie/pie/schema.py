from __future__ import annotations

"""Data model for metadata schema versioning."""

from dataclasses import dataclass

DEFAULT_SCHEMA = "v1"
V2_SCHEMA = "v2"

__all__ = ["Schema", "DEFAULT_SCHEMA", "V2_SCHEMA"]


@dataclass
class Schema:
    """Metadata schema information."""

    schema: str = DEFAULT_SCHEMA
