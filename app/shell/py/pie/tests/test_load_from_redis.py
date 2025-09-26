from pathlib import Path

from pie import index_tree, metadata


def test_build_from_redis_used(monkeypatch):
    path = Path("/doc.yml")

    def fake_get_metadata_by_path(filepath: str, keypath: str):
        assert filepath == str(path)
        assert keypath == "press.id"
        return "doc1"

    calls: list[str] = []

    def fake_build(prefix: str):
        calls.append(prefix)
        return {
            "press": {"id": "doc1"},
            "title": "Title",
            "url": "URL",
            "indextree": {"link": "1", "show": "0"},
        }

    monkeypatch.setattr(index_tree, "get_metadata_by_path", fake_get_metadata_by_path)
    monkeypatch.setattr(metadata, "build_from_redis", fake_build)

    meta = index_tree.load_from_redis(path)

    assert meta == {
        "press": {"id": "doc1"},
        "title": "Title",
        "url": "URL",
        "indextree": {"link": "1", "show": "0"},
    }
    assert calls == ["doc1."]

