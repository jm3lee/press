from __future__ import annotations

from datetime import datetime

import pie.model.metadata as metadata_module

from pie.model import Breadcrumb, Doc, Metadata, Press, PubDate
from pie.schema import DEFAULT_SCHEMA


def test_metadata_to_dict_excludes_missing_url() -> None:
    breadcrumbs = [Breadcrumb("Home", "/"), Breadcrumb("Post")]
    meta = Metadata(
        press=Press(id="post"),
        doc=Doc(
            author="",
            pubdate="2024-01-01",
            title="",
            breadcrumbs=breadcrumbs,
        ),
    )

    assert meta.to_dict() == {
        "doc": {
            "author": "",
            "pubdate": "2024-01-01",
            "title": "",
            "breadcrumbs": [
                {"title": "Home", "url": "/"},
                {"title": "Post"},
            ],
        },
        "press": {"id": "post"},
        "schema": DEFAULT_SCHEMA,
    }


def test_pubdate_from_datetime() -> None:
    moment = datetime(2024, 1, 1)

    pubdate = PubDate(moment)

    assert str(pubdate) == metadata_module.get_pubdate(moment)


def test_pubdate_uses_get_pubdate_for_none(monkeypatch) -> None:
    special = "Jan 02, 2000"
    monkeypatch.setattr(metadata_module, "get_pubdate", lambda date=None: special)

    pubdate = metadata_module.PubDate(None)

    assert str(pubdate) == special


def test_doc_coerces_string_pubdate() -> None:
    doc = Doc(author="", pubdate="Jan 03, 2000", title="")

    assert isinstance(doc.pubdate, PubDate)
    assert doc.to_dict()["pubdate"] == "Jan 03, 2000"


def test_doc_accepts_pubdate_instance() -> None:
    pubdate = PubDate("Jan 04, 2000")

    doc = Doc(author="", pubdate=pubdate, title="")

    assert doc.pubdate is pubdate
    assert doc.to_dict()["pubdate"] == "Jan 04, 2000"
