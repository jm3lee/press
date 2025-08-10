from __future__ import annotations

from pathlib import Path

from pie.update import common


def test_get_changed_files_parses_git_status(monkeypatch: object) -> None:
    """Only tracked modifications are returned."""
    def fake_run(cmd, check, capture_output, text):
        class Result:
            stdout = " M src/doc.md\n?? src/untracked.txt\nA src/doc.yml\n"
        return Result()
    monkeypatch.setattr(common.subprocess, "run", fake_run)

    paths = common.get_changed_files()
    assert paths == [
        Path("src/doc.md"),
        Path("src/doc.yml"),
    ]


def test_replace_field_updates_yaml(tmp_path: Path) -> None:
    """Existing YAML field is replaced and old value returned."""
    yml = tmp_path / "doc.yml"
    yml.write_text("title: T\nauthor: Old\n", encoding="utf-8")

    changed, old = common.replace_field(yml, "author", "New")
    assert changed is True
    assert old == "Old"
    assert "author: New" in yml.read_text(encoding="utf-8")


def test_replace_field_updates_markdown_frontmatter(tmp_path: Path) -> None:
    """Frontmatter field in Markdown is replaced."""
    md = tmp_path / "doc.md"
    md.write_text("---\ntitle: T\nauthor: Old\n---\n", encoding="utf-8")

    changed, old = common.replace_field(md, "author", "New")
    assert changed is True
    assert old == "Old"
    assert "author: New" in md.read_text(encoding="utf-8")


def test_update_files_updates_all_related(tmp_path: Path, monkeypatch: object) -> None:
    """Both Markdown and YAML files are updated for a changed path."""
    src = tmp_path / "src"
    src.mkdir()
    md = src / "doc.md"
    md.write_text("---\ntitle: T\nauthor: Old\n---\n", encoding="utf-8")
    yml = src / "doc.yml"
    yml.write_text("title: T\nauthor: Old\n", encoding="utf-8")

    monkeypatch.chdir(tmp_path)
    messages, checked = common.update_files([Path("src/doc.md")], "author", "New")
    assert checked == 2
    assert set(messages) == {
        "src/doc.md: Old -> New",
        "src/doc.yml: Old -> New",
    }
    assert "author: New" in md.read_text(encoding="utf-8")
    assert "author: New" in yml.read_text(encoding="utf-8")
