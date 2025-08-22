from __future__ import annotations

from pathlib import Path

from pie.check import bad_mathjax as check_bad_mathjax


def test_main_pass(tmp_path: Path) -> None:
    """Markdown without bad delimiters -> exit code 0."""
    md = tmp_path / "index.md"
    md.write_text("$a$ and $$b$$", encoding="utf-8")
    assert check_bad_mathjax.main([str(tmp_path)]) == 0


def test_fail_inline(tmp_path: Path, capsys) -> None:
    """Inline math using \(\) reports an error."""
    md = tmp_path / "index.md"
    md.write_text("text \\(a+b\\)", encoding="utf-8")
    assert check_bad_mathjax.main([str(tmp_path)]) == 1
    captured = capsys.readouterr()
    assert "bad math" in captured.err


def test_fail_display(tmp_path: Path, capsys) -> None:
    """Display math using \[\] reports an error."""
    md = tmp_path / "index.md"
    md.write_text("\\[a+b\\]", encoding="utf-8")
    assert check_bad_mathjax.main([str(tmp_path)]) == 1
    captured = capsys.readouterr()
    assert "bad math" in captured.err
