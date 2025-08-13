from __future__ import annotations

from pathlib import Path

from pie.update import indextree


def test_renames_metadata_key(tmp_path: Path, capsys) -> None:
    """The upgrade script renames 'gen-markdown-index' keys."""

    src = tmp_path / "src"
    src.mkdir()

    yml = src / "doc.yml"
    yml.write_text("gen-markdown-index:\n  show: false\n", encoding="utf-8")

    md = src / "doc.md"
    md.write_text("---\ngen-markdown-index:\n  link: false\n---\n", encoding="utf-8")

    indextree.main([str(src)])

    assert "gen-markdown-index" not in yml.read_text(encoding="utf-8")
    assert "indextree" in yml.read_text(encoding="utf-8")

    assert "gen-markdown-index" not in md.read_text(encoding="utf-8")
    assert "indextree" in md.read_text(encoding="utf-8")

    out_lines = capsys.readouterr().out.strip().splitlines()
    assert f"{yml}: gen-markdown-index -> indextree" in out_lines
    assert f"{md}: gen-markdown-index -> indextree" in out_lines
    assert "2 files checked" in out_lines
    assert "2 files changed" in out_lines

