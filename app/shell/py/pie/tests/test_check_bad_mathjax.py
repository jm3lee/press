from __future__ import annotations

from pathlib import Path
import os

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


def test_exclude_file(tmp_path: Path) -> None:
    """Files listed in the exclude YAML are ignored."""
    bad = tmp_path / "bad.md"
    bad.write_text("text \\(a+b\\)", encoding="utf-8")
    exclude = tmp_path / "exclude.yml"
    exclude.write_text(f"- {bad.name}\n", encoding="utf-8")
    assert check_bad_mathjax.main([str(tmp_path), "-x", str(exclude)]) == 0


def test_exclude_file_wildcard(tmp_path: Path) -> None:
    """Wildcard patterns in the exclude file are honoured."""
    bad = tmp_path / "bad-math.md"
    bad.write_text("text \\(a+b\\)", encoding="utf-8")
    exclude = tmp_path / "exclude.yml"
    exclude.write_text("- bad-*\n", encoding="utf-8")
    assert check_bad_mathjax.main([str(tmp_path), "-x", str(exclude)]) == 0


def test_exclude_file_regex(tmp_path: Path) -> None:
    """Regex patterns in the exclude file are honoured."""
    bad = tmp_path / "bad-1.md"
    bad.write_text("text \\(a+b\\)", encoding="utf-8")
    exclude = tmp_path / "exclude.yml"
    exclude.write_text("- regex:bad-\\d\\.md\n", encoding="utf-8")
    assert check_bad_mathjax.main([str(tmp_path), "-x", str(exclude)]) == 0


def test_default_exclude_file(tmp_path: Path) -> None:
    """Default exclude YAML is used when present."""
    bad = tmp_path / "bad.md"
    bad.write_text("text \\(a+b\\)", encoding="utf-8")
    cfg = tmp_path / "cfg"
    cfg.mkdir()
    exclude = cfg / "check-bad-mathjax-exclude.yml"
    exclude.write_text(f"- {bad.name}\n", encoding="utf-8")
    cwd = os.getcwd()
    os.chdir(tmp_path)
    try:
        assert check_bad_mathjax.main([str(tmp_path)]) == 0
    finally:
        os.chdir(cwd)
