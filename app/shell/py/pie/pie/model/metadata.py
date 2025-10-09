from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, List, Optional

from pie.schema import DEFAULT_SCHEMA, V2_SCHEMA
from pie.utils import get_pubdate

__all__ = [
    "Breadcrumb",
    "Doc",
    "Metadata",
    "MetadataV2",
    "Press",
    "PubDate",
]


@dataclass
class Breadcrumb:
    """Single navigation step for document hierarchy."""

    title: str
    url: Optional[str] = None

    def to_dict(self) -> dict[str, str]:
        """Return dictionary representation omitting ``url`` when absent."""

        data = {"title": self.title}
        if self.url is not None:
            data["url"] = self.url
        return data


@dataclass
class Doc:
    """Document specific metadata."""

    author: str
    pubdate: PubDate | str | datetime | None
    title: str
    breadcrumbs: List[Breadcrumb] = field(default_factory=list)

    def __post_init__(self) -> None:
        """Normalise ``pubdate`` to :class:`PubDate`."""

        if not isinstance(self.pubdate, PubDate):
            self.pubdate = PubDate(self.pubdate)

    def to_dict(self) -> dict[str, Any]:
        """Return dictionary representation for serialization."""

        return {
            "author": self.author,
            "pubdate": str(self.pubdate),
            "title": self.title,
            "breadcrumbs": [b.to_dict() for b in self.breadcrumbs],
        }


@dataclass
class PubDate:
    """Model representing ``doc.pubdate`` values."""

    value: str | datetime | None = field(default_factory=get_pubdate)

    def __post_init__(self) -> None:
        if isinstance(self.value, PubDate):
            self.value = str(self.value)
        elif isinstance(self.value, datetime) or self.value is None:
            self.value = get_pubdate(self.value)
        elif not isinstance(self.value, str):
            self.value = str(self.value)

    def __str__(self) -> str:
        return str(self.value)


@dataclass
class Metadata:
    """Top-level metadata for a document."""

    id: str
    doc: Doc
    schema: str = DEFAULT_SCHEMA
    description: Optional[str] = None

    def to_dict(self) -> dict[str, Any]:
        """Return dictionary representation for serialization."""

        data = {
            "doc": self.doc.to_dict(),
            "id": self.id,
            "schema": self.schema,
        }
        if self.description:
            data["description"] = self.description
        return data


@dataclass
class Press:
    """Press specific metadata for schema ``v2``."""

    id: str
    schema: str = V2_SCHEMA
    author: Optional[str] = None
    title: Optional[str] = None
    pubdate: PubDate | str | datetime | None = None
    mathjax: bool = False

    def __post_init__(self) -> None:
        """Ensure the schema version matches ``v2`` and normalise fields."""

        if self.schema != V2_SCHEMA:
            msg = "press.schema must be 'v2'"
            raise ValueError(msg)
        if self.pubdate is not None and not isinstance(self.pubdate, PubDate):
            self.pubdate = PubDate(self.pubdate)

    def to_dict(self) -> dict[str, Any]:
        """Return dictionary representation for serialization."""

        data: dict[str, Any] = {
            "id": self.id,
            "schema": self.schema,
            "mathjax": self.mathjax,
        }
        if self.author is not None:
            data["author"] = self.author
        if self.title is not None:
            data["title"] = self.title
        if self.pubdate is not None:
            data["pubdate"] = str(self.pubdate)
        return data


@dataclass
class MetadataV2:
    """Metadata schema ``v2`` exposing only the ``press`` namespace."""

    press: Press

    def to_dict(self) -> dict[str, Any]:
        """Return dictionary representation containing only ``press``."""

        return {"press": self.press.to_dict()}
