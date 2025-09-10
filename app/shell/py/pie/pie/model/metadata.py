from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, List, Optional

from pie.schema import DEFAULT_SCHEMA

__all__ = ["Breadcrumb", "Doc", "Metadata"]


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
    pubdate: str
    title: str

    def to_dict(self) -> dict[str, str]:
        """Return dictionary representation for serialization."""

        return {
            "author": self.author,
            "pubdate": self.pubdate,
            "title": self.title,
        }


@dataclass
class Metadata:
    """Top-level metadata for a document."""

    id: str
    doc: Doc
    breadcrumbs: List[Breadcrumb] = field(default_factory=list)
    schema: str = DEFAULT_SCHEMA
    description: Optional[str] = None

    def to_dict(self) -> dict[str, Any]:
        """Return dictionary representation for serialization."""

        data = {
            "breadcrumbs": [b.to_dict() for b in self.breadcrumbs],
            "doc": self.doc.to_dict(),
            "id": self.id,
            "schema": self.schema,
        }
        if self.description:
            data["description"] = self.description
        return data
