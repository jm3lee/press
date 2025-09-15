from __future__ import annotations

from pathlib import Path
import io
import pytest
from typing import Any, Iterable

from ruamel.yaml import YAML

yaml = YAML(typ="safe")

from pie.update import metadata as update_metadata


def test_adds_metadata_from_file(tmp_path: Path, monkeypatch, capsys) -> None:
    """YAML from a file is merged into metadata."""
    src = tmp_path / "src"
    src.mkdir()
    yml = src / "doc.yml"
    yml.write_text("title: Test\n", encoding="utf-8")
    data_file = tmp_path / "add.yml"
    data_file.write_text("foo:\n  bar: a\n", encoding="utf-8")

    monkeypatch.chdir(tmp_path)
    update_metadata.main(["-f", str(data_file), "src/doc.yml"])

    assert yaml.load(yml.read_text(encoding="utf-8")) == {
        "title": "Test",
        "foo": {"bar": "a"},
    }
    captured = capsys.readouterr()
    assert captured.out == ""
    log_text = (
        tmp_path / "log/update-metadata.txt"
    ).read_text(encoding="utf-8")
    assert "src/doc.yml updated" in log_text
    assert "Summary {'checked': 1, 'changed_count': 1}" in log_text


def test_reads_yaml_from_stdin(tmp_path: Path, monkeypatch, capsys) -> None:
    """Input is read from stdin when -f is not given."""
    src = tmp_path / "src"
    src.mkdir()
    yml = src / "doc.yml"
    yml.write_text("title: Test\n", encoding="utf-8")

    monkeypatch.chdir(tmp_path)
    monkeypatch.setattr(
        update_metadata.sys, "stdin", io.StringIO("foo:\n  - a\n  - b\n")
    )
    update_metadata.main(["src/doc.yml"])

    assert yaml.load(yml.read_text(encoding="utf-8")) == {
        "title": "Test",
        "foo": ["a", "b"],
    }
    captured = capsys.readouterr()
    assert captured.out == ""


def test_conflict_skips_file(tmp_path: Path, monkeypatch, capsys) -> None:
    """Conflicting keys result in a warning and no changes."""
    src = tmp_path / "src"
    src.mkdir()
    yml = src / "doc.yml"
    yml.write_text("foo: 1\n", encoding="utf-8")
    data_file = tmp_path / "add.yml"
    data_file.write_text("foo: 2\n", encoding="utf-8")

    monkeypatch.chdir(tmp_path)
    code = update_metadata.main(["-f", str(data_file), "src/doc.yml"])

    assert code == 1
    assert yaml.load(yml.read_text(encoding="utf-8")) == {"foo": 1}
    captured = capsys.readouterr()
    assert captured.out == ""
    log_text = (
        tmp_path / "log/update-metadata.txt"
    ).read_text(encoding="utf-8")
    assert "Conflict merging metadata for src/doc.yml" in log_text
    assert "Summary {'checked': 1, 'changed_count': 0}" in log_text


def test_merge_handles_nested_structures() -> None:
    """Merging dictionaries and lists deduplicates values."""
    a = {"foo": {"bar": 1}, "list": ["a"]}
    b = {"foo": {"baz": 2}, "list": ["a", "b"]}
    merged, conflict = update_metadata._merge(a, b)
    assert not conflict
    assert merged == {"foo": {"bar": 1, "baz": 2}, "list": ["a", "b"]}


def test_merge_none_and_equal_values() -> None:
    """None and equal values are handled without conflict."""
    merged, conflict = update_metadata._merge(None, {"a": 1})
    assert merged == {"a": 1} and not conflict
    merged, conflict = update_metadata._merge("x", "x")
    assert merged == "x" and not conflict


def test_merge_file_no_change_yaml(tmp_path: Path) -> None:
    """Unchanged YAML returns without conflict."""
    fp = tmp_path / "doc.yml"
    fp.write_text("a: 1\n", encoding="utf-8")
    changed, conflict = update_metadata._merge_file(fp, {"a": 1}, False)
    assert (changed, conflict) == (False, False)


def test_merge_file_markdown_frontmatter(tmp_path: Path) -> None:
    """Markdown frontmatter is updated when present."""
    md = tmp_path / "doc.md"
    md.write_text("---\nfoo: 1\n---\nbody\n", encoding="utf-8")
    changed, conflict = update_metadata._merge_file(md, {"bar": 2}, False)
    assert changed and not conflict
    text = md.read_text(encoding="utf-8")
    frontmatter = text.split("---\n")[1]
    assert yaml.load(frontmatter) == {"foo": 1, "bar": 2}


def test_merge_file_markdown_adds_frontmatter(tmp_path: Path) -> None:
    """Frontmatter is added when missing from markdown."""
    md = tmp_path / "doc.md"
    md.write_text("content\n", encoding="utf-8")
    changed, conflict = update_metadata._merge_file(md, {"foo": 1}, False)
    assert changed and not conflict
    text = md.read_text(encoding="utf-8")
    frontmatter = text.split("---\n")[1]
    assert yaml.load(frontmatter) == {"foo": 1}


def test_merge_file_markdown_conflict(tmp_path: Path) -> None:
    """Unterminated frontmatter reports a conflict."""
    md = tmp_path / "doc.md"
    md.write_text("---\nfoo: 1\ncontent\n", encoding="utf-8")
    changed, conflict = update_metadata._merge_file(md, {"bar": 2}, False)
    assert not changed and conflict


def test_read_data_requires_mapping(tmp_path: Path) -> None:
    """_read_data exits when YAML is not a mapping."""
    bad = tmp_path / "bad.yml"
    bad.write_text("- a\n- b\n", encoding="utf-8")
    with pytest.raises(SystemExit):
        update_metadata._read_data(bad)


def test_update_files_skips_duplicate_and_missing(
    tmp_path: Path, monkeypatch
) -> None:
    """Duplicate bases and missing files are skipped."""
    md = tmp_path / "doc.md"
    md.write_text("content\n", encoding="utf-8")
    other = tmp_path / "doc.yml"
    other.write_text("foo: 1\n", encoding="utf-8")

    def fake_load_metadata_pair(path: Path) -> dict:
        return {"path": ["missing.md"]}

    monkeypatch.setattr(
        update_metadata, "load_metadata_pair", fake_load_metadata_pair
    )
    messages, checked, conflict = update_metadata.update_files(
        [md, other], {"foo": 2}, False
    )
    assert messages == [f"{md} updated"]
    assert checked == 1
    assert not conflict


def test_main_uses_get_changed_files(tmp_path: Path, monkeypatch) -> None:
    """When no paths are given git changes are used."""
    data_file = tmp_path / "add.yml"
    data_file.write_text("foo: 1\n", encoding="utf-8")
    target = tmp_path / "doc.yml"
    target.write_text("foo: 1\n", encoding="utf-8")

    monkeypatch.chdir(tmp_path)

    called: dict[str, Any] = {}

    def fake_get_changed_files() -> list[Path]:
        called["called"] = True
        return [target]

    monkeypatch.setattr(
        update_metadata, "get_changed_files", fake_get_changed_files
    )

    def fake_update_files(paths: Iterable[Path], data: dict, sort_keys: bool):
        called["paths"] = list(paths)
        return [], 0, False

    monkeypatch.setattr(update_metadata, "update_files", fake_update_files)
    update_metadata.main(["-f", str(data_file)])
    assert called["called"]
    assert called["paths"] == [target]

