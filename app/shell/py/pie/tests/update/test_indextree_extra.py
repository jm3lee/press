from __future__ import annotations

from pathlib import Path

from pie.update import indextree


def test_upgrade_yaml_without_section(tmp_path: Path) -> None:
    yml = tmp_path / "doc.yml"
    yml.write_text("title: test\n", encoding="utf-8")
    assert indextree._upgrade_yaml(yml) is False


def test_upgrade_markdown_without_front_matter(tmp_path: Path) -> None:
    md = tmp_path / "doc.md"
    md.write_text("content only\n", encoding="utf-8")
    assert indextree._upgrade_markdown(md) is False


def test_upgrade_markdown_missing_end(tmp_path: Path) -> None:
    md = tmp_path / "doc.md"
    md.write_text("---\nkey: value\n", encoding="utf-8")
    assert indextree._upgrade_markdown(md) is False


def test_upgrade_markdown_without_section(tmp_path: Path) -> None:
    md = tmp_path / "doc.md"
    md.write_text("---\ntitle: test\n---\n", encoding="utf-8")
    assert indextree._upgrade_markdown(md) is False


def test_upgrade_file_other_suffix(tmp_path: Path) -> None:
    txt = tmp_path / "doc.txt"
    txt.write_text("", encoding="utf-8")
    assert indextree.upgrade_file(txt) is False


def test_walk_files_with_file(tmp_path: Path) -> None:
    file_path = tmp_path / "note.md"
    file_path.write_text("---\n---\n", encoding="utf-8")
    paths = list(indextree.walk_files([file_path]))
    assert paths == [file_path]
