from __future__ import annotations

from pathlib import Path

from pie.update import author as update_author


def test_updates_yaml_from_markdown_change(tmp_path: Path, monkeypatch, capsys) -> None:
    """Changing Markdown updates author in paired YAML."""
    src = tmp_path / "src"
    src.mkdir()
    md = src / "doc.md"
    md.write_text("---\ntitle: Test\n---\n", encoding="utf-8")
    yml = src / "doc.yml"
    yml.write_text(
        "title: Test\nauthor: Jane Doe\n",
        encoding="utf-8",
    )

    cfg = tmp_path / "cfg"
    cfg.mkdir()
    (cfg / "update-author.yml").write_text("author: Brian Lee\n", encoding="utf-8")

    monkeypatch.chdir(tmp_path)
    monkeypatch.setattr(update_author, "get_changed_files", lambda: [Path("src/doc.md")])

    update_author.main([])
    assert "author: Brian Lee" in yml.read_text(encoding="utf-8")
    expected_line = "src/doc.yml: Jane Doe -> Brian Lee"
    captured = capsys.readouterr()
    assert captured.out.strip().splitlines() == [
        expected_line,
        "2 files checked",
        "1 file changed",
    ]
    log_text = (tmp_path / "log/update-author.txt").read_text(encoding="utf-8")
    assert expected_line in log_text


def test_updates_markdown_frontmatter(tmp_path: Path, monkeypatch, capsys) -> None:
    """Author in Markdown frontmatter is replaced."""
    src = tmp_path / "src"
    src.mkdir()
    md = src / "doc.md"
    md.write_text(
        "---\ntitle: Test\nauthor: Jane Doe\n---\nbody\n",
        encoding="utf-8",
    )

    cfg = tmp_path / "cfg"
    cfg.mkdir()
    (cfg / "update-author.yml").write_text("author: Brian Lee\n", encoding="utf-8")

    monkeypatch.chdir(tmp_path)
    monkeypatch.setattr(update_author, "get_changed_files", lambda: [Path("src/doc.md")])

    update_author.main([])
    assert "author: Brian Lee" in md.read_text(encoding="utf-8")
    expected_line = "src/doc.md: Jane Doe -> Brian Lee"
    captured = capsys.readouterr()
    assert captured.out.strip().splitlines() == [
        expected_line,
        "1 file checked",
        "1 file changed",
    ]
    log_text = (tmp_path / "log/update-author.txt").read_text(encoding="utf-8")
    assert expected_line in log_text


def test_ignores_author_in_body(tmp_path: Path, monkeypatch, capsys) -> None:
    """Author outside frontmatter is ignored."""
    src = tmp_path / "src"
    src.mkdir()
    md = src / "doc.md"
    md.write_text("---\ntitle: Test\n---\nbody\nauthor: Jane Doe\n", encoding="utf-8")

    cfg = tmp_path / "cfg"
    cfg.mkdir()
    (cfg / "update-author.yml").write_text("author: Brian Lee\n", encoding="utf-8")

    monkeypatch.chdir(tmp_path)
    monkeypatch.setattr(update_author, "get_changed_files", lambda: [Path("src/doc.md")])

    update_author.main([])
    assert "Jane Doe" in md.read_text(encoding="utf-8")
    captured = capsys.readouterr()
    assert captured.out.strip().splitlines() == [
        "1 file checked",
        "0 files changed",
    ]

