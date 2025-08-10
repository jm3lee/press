import os
from pathlib import Path

from pie import index_tree
import pie.metadata as metadata
from pie.metadata import (
    fill_missing_metadata,
    get_metadata_by_path,
    read_from_markdown,
    read_from_yaml,
)


def test_read_from_markdown_parses_frontmatter(tmp_path):
    """Frontmatter {'title': 'T'} -> {'title': 'T', 'url': '/doc.html'}."""
    md = tmp_path / 'src' / 'doc.md'
    md.parent.mkdir(parents=True)
    md.write_text('---\n{"title": "T"}\n---\nbody')
    os.chdir(tmp_path)
    try:
        data = read_from_markdown('src/doc.md')
    finally:
        os.chdir('/tmp')
    assert data == {'title': 'T', 'url': '/doc.html'}


def test_read_from_yaml_generates_fields(tmp_path):
    """YAML {'name': 'Foo'} -> metadata with url/id/citation."""
    yml = tmp_path / 'src' / 'item.yml'
    yml.parent.mkdir(parents=True)
    yml.write_text('{"name": "Foo"}')
    os.chdir(tmp_path)
    try:
        data = read_from_yaml('src/item.yml')
    finally:
        os.chdir('/tmp')
    assert data['name'] == 'Foo'
    assert data['url'] == '/item.html'
    assert data['citation'] == 'foo'
    assert data['id'] == 'item'



class DummyRedis:
    def __init__(self, store):
        self.store = store

    def get(self, key):
        return self.store.get(key)


def test_returns_value(monkeypatch):
    store = {"/doc.yml": "doc1", "doc1.title": "Title"}
    monkeypatch.setattr(metadata, "redis_conn", DummyRedis(store))
    assert get_metadata_by_path("/doc.yml", "title") == "Title"


def test_missing_entries(monkeypatch):
    store = {"/doc.yml": "doc1"}
    monkeypatch.setattr(metadata, "redis_conn", DummyRedis(store))
    assert get_metadata_by_path("/doc.yml", "title") is None
    monkeypatch.setattr(metadata, "redis_conn", DummyRedis({}))
    assert get_metadata_by_path("/other.yml", "title") is None


def test_fill_missing_metadata(tmp_path):
    """{'name': 'Foo'} -> url/id/citation."""
    yml = tmp_path / "src" / "item.yml"
    yml.parent.mkdir(parents=True)
    yml.write_text("")
    os.chdir(tmp_path)
    try:
        data = fill_missing_metadata({"name": "Foo"}, filepath="src/item.yml")
    finally:
        os.chdir("/tmp")
    assert data["url"] == "/item.html"
    assert data["citation"] == "foo"
    assert data["id"] == "item"


def test_build_from_redis_used(monkeypatch):
    path = Path("/doc.yml")

    def fake_get_metadata_by_path(filepath: str, keypath: str):
        assert filepath == str(path)
        assert keypath == "id"
        return "doc1"

    calls: list[str] = []

    def fake_build(prefix: str):
        calls.append(prefix)
        return {
            "id": "doc1",
            "title": "Title",
            "url": "URL",
            "gen-markdown-index": {"link": "1", "show": "0"},
        }

    monkeypatch.setattr(index_tree, "get_metadata_by_path", fake_get_metadata_by_path)
    monkeypatch.setattr(index_tree, "build_from_redis", fake_build)

    meta = index_tree.load_from_redis(path)

    assert meta == {
        "id": "doc1",
        "title": "Title",
        "url": "URL",
        "gen-markdown-index": {"link": "1", "show": "0"},
    }
    assert calls == ["doc1."]

