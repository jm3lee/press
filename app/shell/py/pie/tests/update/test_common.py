from __future__ import annotations

from pathlib import Path
import subprocess

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


def test_get_changed_files_missing_git(monkeypatch: object) -> None:
    """Missing git executable returns empty list and warns."""

    def fake_run(cmd, check, capture_output, text):
        raise FileNotFoundError("git not found")

    warned = {"value": False}

    def fake_warning(msg, **kwargs):
        warned["value"] = True

    monkeypatch.setattr(common.subprocess, "run", fake_run)
    monkeypatch.setattr(common.logger, "warning", fake_warning)

    paths = common.get_changed_files()
    assert paths == []
    assert warned["value"] is True


def test_get_changed_files_uninitialized_repo(monkeypatch: object) -> None:
    """Uninitialized repository returns empty list and warns."""

    def fake_run(cmd, check, capture_output, text):
        raise subprocess.CalledProcessError(1, cmd)

    warned = {"value": False}

    def fake_warning(msg, **kwargs):
        warned["value"] = True

    monkeypatch.setattr(common.subprocess, "run", fake_run)
    monkeypatch.setattr(common.logger, "warning", fake_warning)

    paths = common.get_changed_files()
    assert paths == []
    assert warned["value"] is True


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


def test_update_files_prefers_yaml(tmp_path: Path, monkeypatch: object) -> None:
    """Only YAML is updated when both Markdown and YAML exist."""
    src = tmp_path / "src"
    src.mkdir()
    md = src / "doc.md"
    md.write_text("---\ntitle: T\nauthor: Old\n---\n", encoding="utf-8")
    yml = src / "doc.yml"
    yml.write_text("title: T\nauthor: Old\n", encoding="utf-8")

    monkeypatch.chdir(tmp_path)
    messages, checked = common.update_files([Path("src/doc.md")], "author", "New")
    assert checked == 1
    assert set(messages) == {"src/doc.yml: Old -> New"}
    assert "author: Old" in md.read_text(encoding="utf-8")
    assert "author: New" in yml.read_text(encoding="utf-8")
