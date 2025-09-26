from pathlib import Path

from ruamel.yaml import YAML

yaml = YAML(typ="safe")

import pie.gen_markdown_index as gen_markdown_index
from pie.gen_markdown_index import generate, main
from pie import index_tree, metadata


def test_show_property(tmp_path, monkeypatch):
    """Nodes with 'show: false' are skipped."""
    (tmp_path / "alpha.yml").write_text(
        "press:\n  id: alpha\ntitle: Alpha\ndoc:\n  title: Alpha\n"
    )
    (tmp_path / "beta.yml").write_text(
        "press:\n  id: beta\ntitle: Beta\ndoc:\n  title: Beta\n"
        "indextree:\n  show: false\n",
    )
    hidden = tmp_path / "hidden"
    hidden.mkdir()
    (hidden / "index.yml").write_text(
        "press:\n  id: hidden\ntitle: Hidden\ndoc:\n  title: Hidden\n"
        "indextree:\n  show: false\n",
    )
    (hidden / "child.yml").write_text(
        "press:\n  id: child\ntitle: Child\ndoc:\n  title: Child\n"
    )

    def fake_meta(filepath: str, keypath: str):
        data = yaml.load(Path(filepath).read_text()) or {}
        press = data.get("press")
        if not isinstance(press, dict):
            press = {}
            data["press"] = press
        press.setdefault("id", Path(filepath).with_suffix("").name)
        if "doc" not in data and "title" in data:
            data["doc"] = {"title": data["title"]}
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
            data = yaml.load(p.read_text()) or {}
            if "doc" not in data and "title" in data:
                data["doc"] = {"title": data["title"]}
            press = data.get("press")
            if not isinstance(press, dict):
                press = {}
                data["press"] = press
            if press.get("id", p.with_suffix("").name) == doc_id:
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
    (tmp_path / "foo.yml").write_text("title: Foo\ndoc:\n  title: Foo\n")

    def fake_meta(filepath: str, keypath: str):
        data = yaml.load(Path(filepath).read_text()) or {}
        press = data.get("press")
        if not isinstance(press, dict):
            press = {}
            data["press"] = press
        press.setdefault("id", Path(filepath).with_suffix("").name)
        if "doc" not in data and "title" in data:
            data["doc"] = {"title": data["title"]}
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
            data = yaml.load(p.read_text()) or {}
            if "doc" not in data and "title" in data:
                data["doc"] = {"title": data["title"]}
            press = data.get("press")
            if not isinstance(press, dict):
                press = {}
                data["press"] = press
            if press.get("id", p.with_suffix("").name) == doc_id:
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
        "press": {"id": "alpha"},
        "title": "Alpha",
        "doc": {"title": "Alpha"},
        "indextree": {"link": False},
    }
    meta_group = {
        "press": {"id": "group"},
        "title": "Group",
        "doc": {"title": "Group"},
    }
    meta_child = {
        "press": {"id": "child"},
        "title": "Child",
        "doc": {"title": "Child"},
    }

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


def test_numeric_filenames_sort(tmp_path, monkeypatch):
    """Files named numerically appear in numerical order."""
    (tmp_path / "1.yml").write_text(
        "press:\n  id: one\ntitle: Beta\ndoc:\n  title: Beta\n"
    )
    (tmp_path / "2.yml").write_text(
        "press:\n  id: two\ntitle: Alpha\ndoc:\n  title: Alpha\n"
    )

    def fake_meta(filepath: str, keypath: str):
        data = yaml.load(Path(filepath).read_text()) or {}
        press = data.get("press")
        if not isinstance(press, dict):
            press = {}
            data["press"] = press
        press.setdefault("id", Path(filepath).with_suffix("").name)
        if "doc" not in data and "title" in data:
            data["doc"] = {"title": data["title"]}
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
            data = yaml.load(p.read_text()) or {}
            if "doc" not in data and "title" in data:
                data["doc"] = {"title": data["title"]}
            press = data.get("press")
            if not isinstance(press, dict):
                press = {}
                data["press"] = press
            if press.get("id", p.with_suffix("").name) == doc_id:
                return data
        return None

    monkeypatch.setattr(metadata, "build_from_redis", fake_build)

    lines = list(generate(tmp_path))

    assert lines == [
        '- {{ linktitle("one") }}',
        '- {{ linktitle("two") }}',
    ]


def test_main_prints_generated_index(tmp_path, monkeypatch, capsys):
    """The ``main`` function prints generated lines."""
    path = tmp_path / "foo.yml"
    meta = {
        "press": {"id": "foo"},
        "title": "Foo",
        "doc": {"title": "Foo"},
    }

    def fake_walk(directory):
        return [(meta, path)]

    monkeypatch.setattr(gen_markdown_index, "walk", fake_walk)

    main([str(tmp_path)])
    captured = capsys.readouterr()
    assert captured.out == '- {{ linktitle("foo") }}\n'
