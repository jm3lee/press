from pathlib import Path

import yaml

from pie.gen_markdown_index import generate
from pie import index_tree, metadata


def test_show_property(tmp_path, monkeypatch):
    """Nodes with 'show: false' are skipped."""
    (tmp_path / "alpha.yml").write_text("id: alpha\ntitle: Alpha\n")
    (tmp_path / "beta.yml").write_text(
        "id: beta\ntitle: Beta\n" "gen-markdown-index:\n  show: false\n",
    )
    hidden = tmp_path / "hidden"
    hidden.mkdir()
    (hidden / "index.yml").write_text(
        "id: hidden\ntitle: Hidden\n" "gen-markdown-index:\n  show: false\n",
    )
    (hidden / "child.yml").write_text("id: child\ntitle: Child\n")

    def fake_meta(filepath: str, keypath: str):
        data = yaml.safe_load(Path(filepath).read_text()) or {}
        if "id" not in data:
            data["id"] = Path(filepath).with_suffix("").name
        for key in keypath.split("."):
            if not isinstance(data, dict):
                return None
            data = data.get(key)
            if data is None:
                return None
        return data

    monkeypatch.setattr(index_tree, "get_metadata_by_path", fake_meta)

    def fake_build(prefix: str):
        doc_id = prefix.rstrip(".")
        for p in tmp_path.rglob("*.yml"):
            data = yaml.safe_load(p.read_text()) or {}
            if data.get("id", p.with_suffix("").name) == doc_id:
                return data
        return None

    monkeypatch.setattr(metadata, "build_from_redis", fake_build)

    lines = list(generate(tmp_path))
    assert lines == [
        '- {{"alpha"|linktitle}}',
        '- {{"child"|linktitle}}',
    ]


def test_missing_id_uses_filename(tmp_path, monkeypatch):
    """Files without an explicit id derive it from the filename."""
    (tmp_path / "foo.yml").write_text("title: Foo\n")

    def fake_meta(filepath: str, keypath: str):
        data = yaml.safe_load(Path(filepath).read_text()) or {}
        if "id" not in data:
            data["id"] = Path(filepath).with_suffix("").name
        for key in keypath.split("."):
            if not isinstance(data, dict):
                return None
            data = data.get(key)
            if data is None:
                return None
        return data

    monkeypatch.setattr(index_tree, "get_metadata_by_path", fake_meta)

    def fake_build(prefix: str):
        doc_id = prefix.rstrip(".")
        for p in tmp_path.rglob("*.yml"):
            data = yaml.safe_load(p.read_text()) or {}
            if data.get("id", p.with_suffix("").name) == doc_id:
                return data
        return None

    monkeypatch.setattr(metadata, "build_from_redis", fake_build)

    lines = list(generate(tmp_path))

    assert lines == ['- {{"foo"|linktitle}}']
