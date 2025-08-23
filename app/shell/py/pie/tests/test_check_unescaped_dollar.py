from __future__ import annotations

from __future__ import annotations

from pathlib import Path
import os

from pie.check import unescaped_dollar as check_unescaped_dollar


def test_main_pass(tmp_path: Path) -> None:
    """Markdown with escaped dollars passes."""
    md = tmp_path / "index.md"
    md.write_text("$a$ and \\$5", encoding="utf-8")
    assert check_unescaped_dollar.main([str(tmp_path)]) == 0


def test_fail(tmp_path: Path, capsys) -> None:
    """Single unescaped dollars report an error."""
    md = tmp_path / "index.md"
    md.write_text("Cost $5", encoding="utf-8")
    assert check_unescaped_dollar.main([str(tmp_path)]) == 1
    captured = capsys.readouterr()
    assert "dollar sign" in captured.err


def test_exclude_file(tmp_path: Path) -> None:
    """Files listed in the exclude YAML are ignored."""
    bad = tmp_path / "bad.md"
    bad.write_text("Cost $5", encoding="utf-8")
    exclude = tmp_path / "exclude.yml"
    exclude.write_text(f"- {bad.name}\n", encoding="utf-8")
    assert check_unescaped_dollar.main([str(tmp_path), "-x", str(exclude)]) == 0


def test_default_exclude_file(tmp_path: Path) -> None:
    """Default exclude YAML is used when present."""
    bad = tmp_path / "bad.md"
    bad.write_text("Cost $5", encoding="utf-8")
    cfg = tmp_path / "cfg"
    cfg.mkdir()
    exclude = cfg / "check-unescaped-dollar-exclude.yml"
    exclude.write_text(f"- {bad.name}\n", encoding="utf-8")
    cwd = os.getcwd()
    os.chdir(tmp_path)
    try:
        assert check_unescaped_dollar.main([str(tmp_path)]) == 0
    finally:
        os.chdir(cwd)
