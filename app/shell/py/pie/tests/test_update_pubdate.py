from __future__ import annotations

from datetime import datetime
from pathlib import Path

from pie import update_pubdate


def test_updates_yaml_from_markdown_change(tmp_path: Path, monkeypatch, capsys) -> None:
    """Changing Markdown updates pubdate in paired YAML."""
    src = tmp_path / "src"
    src.mkdir()
    md = src / "doc.md"
    md.write_text("---\ntitle: Test\n---\n", encoding="utf-8")
    yml = src / "doc.yml"
    yml.write_text(
        "name: Test\ntitle: Test\npubdate: Jan 01, 2000\n",
        encoding="utf-8",
    )

    monkeypatch.chdir(tmp_path)
    monkeypatch.setattr(update_pubdate, "get_changed_files", lambda: [Path("src/doc.md")])

    update_pubdate.main([])
    expected = datetime.now().strftime("%b %d, %Y")
    assert f"pubdate: {expected}" in yml.read_text(encoding="utf-8")
    expected_line = f"src/doc.yml: Jan 01, 2000 -> {expected}"
    captured = capsys.readouterr()
    assert captured.out.strip() == expected_line
    log_text = (tmp_path / "log/update-pubdate.txt").read_text(encoding="utf-8")
    assert expected_line in log_text


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
    expected = datetime.now().strftime("%b %d, %Y")
    assert f"pubdate: {expected}" in md.read_text(encoding="utf-8")
    expected_line = f"src/doc.md: Jan 01, 2000 -> {expected}"
    captured = capsys.readouterr()
    assert captured.out.strip() == expected_line
    log_text = (tmp_path / "log/update-pubdate.txt").read_text(encoding="utf-8")
    assert expected_line in log_text


def test_ignores_pubdate_in_body(tmp_path: Path, monkeypatch, capsys) -> None:
    """Pubdate outside frontmatter is ignored."""
    src = tmp_path / "src"
    src.mkdir()
    md = src / "doc.md"
    md.write_text("---\ntitle: Test\n---\nbody\npubdate: Jan 01, 2000\n", encoding="utf-8")

    monkeypatch.chdir(tmp_path)
    monkeypatch.setattr(update_pubdate, "get_changed_files", lambda: [Path("src/doc.md")])

    update_pubdate.main([])
    assert "Jan 01, 2000" in md.read_text(encoding="utf-8")
    captured = capsys.readouterr()
    assert captured.out.strip() == ""


def test_warns_when_pubdate_missing(tmp_path: Path, monkeypatch) -> None:
    """A warning is logged when pubdate can't be updated for a src file."""
    src = tmp_path / "src"
    src.mkdir()
    md = src / "doc.md"
    md.write_text("---\ntitle: Test\n---\n", encoding="utf-8")

    monkeypatch.chdir(tmp_path)
    monkeypatch.setattr(update_pubdate, "get_changed_files", lambda: [Path("src/doc.md")])

    warnings: list[str] = []
    handle = update_pubdate.logger.add(warnings.append, level="WARNING")
    try:
        update_pubdate.main([])
    finally:
        update_pubdate.logger.remove(handle)

    assert any("pubdate not updated" in m for m in warnings)
