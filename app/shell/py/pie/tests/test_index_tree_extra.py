from __future__ import annotations

from pathlib import Path

import pytest

from pie import index_tree


def test_load_from_redis_no_doc(monkeypatch, tmp_path):
    """Return None when metadata id lookup fails."""

    def fake_get_metadata_by_path(filepath: str, key: str) -> str | None:
        return None

    called = {}

    def fake_debug(msg: str, **kwargs) -> None:
        called["msg"] = msg
        called["kwargs"] = kwargs

    monkeypatch.setattr(index_tree, "get_metadata_by_path", fake_get_metadata_by_path)
    monkeypatch.setattr(index_tree.logger, "debug", fake_debug)

    result = index_tree.load_from_redis(tmp_path / "doc.yml")

    assert result is None
    assert called["msg"] == "No doc_id found"


def test_walk_warns_and_raises(tmp_path: Path):
    """walk emits a warning and propagates loader exceptions."""

    target = tmp_path / "file.yml"
    target.write_text("", encoding="utf-8")

    def loader(_path: Path):
        raise RuntimeError("boom")

    with pytest.raises(RuntimeError), pytest.warns(UserWarning, match="Failed to process"):
        list(index_tree.walk(tmp_path, loader))


def test_sort_entries_order_priority():
    """Explicit ``indextree.order`` is prioritized in sorting."""

    entries = [
        (
            {"title": "B", "doc": {"title": "B"}, "indextree": {"order": 1}},
            Path("b"),
        ),
        ({"title": "A", "doc": {"title": "A"}}, Path("a")),
    ]

    index_tree.sort_entries(entries)

    assert entries[0][0]["title"] == "B"
