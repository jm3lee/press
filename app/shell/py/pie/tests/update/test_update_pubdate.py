from __future__ import annotations

from pathlib import Path

from pie.update import pubdate as update_pubdate
from pie.utils import get_pubdate


def test_updates_yaml_from_markdown_change(tmp_path: Path, monkeypatch, capsys) -> None:
    """Changing Markdown updates pubdate in paired YAML."""
    src = tmp_path / "src"
    src.mkdir()
    md = src / "doc.md"
    md.write_text("---\ntitle: Test\n---\n", encoding="utf-8")
    yml = src / "doc.yml"
    yml.write_text(
        "title: Test\npubdate: Jan 01, 2000\n",
        encoding="utf-8",
    )

    monkeypatch.chdir(tmp_path)
    monkeypatch.setattr(update_pubdate, "get_changed_files", lambda: [Path("src/doc.md")])

    update_pubdate.main([])
    expected = get_pubdate()
    assert f"pubdate: {expected}" in yml.read_text(encoding="utf-8")
    assert f"pubdate: {expected}" in md.read_text(encoding="utf-8")
    captured = capsys.readouterr()
    lines = captured.out.strip().splitlines()
    assert f"src/doc.md: undefined -> {expected}" in lines
    assert f"src/doc.yml: Jan 01, 2000 -> {expected}" in lines
    assert "2 files checked" in lines
    assert "2 files changed" in lines
    assert len(lines) == 4
    log_text = (tmp_path / "log/update-pubdate.txt").read_text(encoding="utf-8")
    assert f"src/doc.md: undefined -> {expected}" in log_text
    assert f"src/doc.yml: Jan 01, 2000 -> {expected}" in log_text


def test_updates_markdown_frontmatter(tmp_path: Path, monkeypatch, capsys) -> None:
    """Pubdate in Markdown frontmatter is replaced."""
    src = tmp_path / "src"
    src.mkdir()
    md = src / "doc.md"
    md.write_text(
        "---\ntitle: Test\npubdate: Jan 01, 2000\n---\nbody\n",
        encoding="utf-8",
    )

    monkeypatch.chdir(tmp_path)
    monkeypatch.setattr(update_pubdate, "get_changed_files", lambda: [Path("src/doc.md")])

    update_pubdate.main([])
    expected = get_pubdate()
    assert f"pubdate: {expected}" in md.read_text(encoding="utf-8")
    expected_line = f"src/doc.md: Jan 01, 2000 -> {expected}"
    captured = capsys.readouterr()
    assert captured.out.strip().splitlines() == [
        expected_line,
        "1 file checked",
        "1 file changed",
    ]
    log_text = (tmp_path / "log/update-pubdate.txt").read_text(encoding="utf-8")
    assert expected_line in log_text


def test_adds_frontmatter_when_pubdate_in_body(tmp_path: Path, monkeypatch, capsys) -> None:
    """Pubdate outside frontmatter is ignored and field added to frontmatter."""
    src = tmp_path / "src"
    src.mkdir()
    md = src / "doc.md"
    md.write_text("---\ntitle: Test\n---\nbody\npubdate: Jan 01, 2000\n", encoding="utf-8")

    monkeypatch.chdir(tmp_path)
    monkeypatch.setattr(update_pubdate, "get_changed_files", lambda: [Path("src/doc.md")])

    update_pubdate.main([])
    expected = get_pubdate()
    text = md.read_text(encoding="utf-8")
    assert f"pubdate: {expected}" in text
    assert "pubdate: Jan 01, 2000" in text
    captured = capsys.readouterr()
    assert captured.out.strip().splitlines() == [
        f"src/doc.md: undefined -> {expected}",
        "1 file checked",
        "1 file changed",
    ]
