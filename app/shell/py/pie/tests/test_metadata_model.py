from __future__ import annotations

from pie.model import Breadcrumb, Doc, Metadata
from pie.schema import DEFAULT_SCHEMA


def test_metadata_to_dict_excludes_missing_url() -> None:
    breadcrumbs = [Breadcrumb("Home", "/"), Breadcrumb("Post")]
    meta = Metadata(
        id="post",
        doc=Doc(author="", pubdate="2024-01-01", title=""),
        breadcrumbs=breadcrumbs,
    )

    assert meta.to_dict() == {
        "breadcrumbs": [
            {"title": "Home", "url": "/"},
            {"title": "Post"},
        ],
        "doc": {"author": "", "pubdate": "2024-01-01", "title": ""},
        "id": "post",
        "schema": DEFAULT_SCHEMA,
    }
