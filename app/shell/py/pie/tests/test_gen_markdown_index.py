from pathlib import Path

import yaml

import pie.gen_markdown_index as gen_markdown_index
from pie.gen_markdown_index import generate, main
from pie import index_tree, metadata


def test_show_property(tmp_path, monkeypatch):
    """Nodes with 'show: false' are skipped."""
    (tmp_path / "alpha.yml").write_text("id: alpha\ntitle: Alpha\n")
    (tmp_path / "beta.yml").write_text(
        "id: beta\ntitle: Beta\n" "indextree:\n  show: false\n",
    )
    hidden = tmp_path / "hidden"
    hidden.mkdir()
    (hidden / "index.yml").write_text(
        "id: hidden\ntitle: Hidden\n" "indextree:\n  show: false\n",
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
        '- {{ linktitle("alpha") }}',
        '- {{ linktitle("child") }}',
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

    assert lines == ['- {{ linktitle("foo") }}']


def test_link_false_and_recursion(tmp_path, monkeypatch):
    """Entries honour the 'link' option and recurse into subdirectories."""
    group_dir = tmp_path / "group"
    group_dir.mkdir()
    child_file = group_dir / "child.yml"
    child_file.touch()

    meta_alpha = {
        "id": "alpha",
        "title": "Alpha",
        "indextree": {"link": False},
    }
    meta_group = {"id": "group", "title": "Group"}
    meta_child = {"id": "child", "title": "Child"}

    def fake_walk(directory):
        if directory == tmp_path:
            return [(meta_alpha, tmp_path / "alpha.yml"), (meta_group, group_dir)]
        if directory == group_dir:
            return [(meta_child, child_file)]
        return []

    monkeypatch.setattr(gen_markdown_index, "walk", fake_walk)

    lines = list(generate(tmp_path))

    assert lines == [
        "- {{'Alpha'|title}}",
        '- {{ linktitle("group") }}',
        '  - {{ linktitle("child") }}',
    ]


def test_main_prints_generated_index(tmp_path, monkeypatch, capsys):
    """The ``main`` function prints generated lines."""
    path = tmp_path / "foo.yml"
    meta = {"id": "foo", "title": "Foo"}

    def fake_walk(directory):
        return [(meta, path)]

    monkeypatch.setattr(gen_markdown_index, "walk", fake_walk)

    main([str(tmp_path)])
    captured = capsys.readouterr()
    assert captured.out == '- {{ linktitle("foo") }}\n'
