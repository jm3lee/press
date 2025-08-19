from __future__ import annotations

from pathlib import Path

from pie.check import underscores as check_underscores


def test_main_pass(tmp_path: Path) -> None:
    """URL without underscore -> exit code 0."""
    html = tmp_path / "index.html"
    html.write_text('<a href="foo-bar.html">link</a>', encoding="utf-8")
    assert check_underscores.main([str(tmp_path)]) == 0


def test_main_fail(tmp_path: Path, capsys) -> None:
    """URL with underscore -> exit code 1 and report URL."""
    html = tmp_path / "index.html"
    html.write_text('<a href="foo_bar.html">link</a>', encoding="utf-8")
    assert check_underscores.main([str(tmp_path)]) == 1
    captured = capsys.readouterr()
    assert "foo_bar.html" in captured.err
    assert "dashes" in captured.err


def test_main_fail_src(tmp_path: Path, capsys) -> None:
    """Underscore in ``src`` attribute is reported."""
    html = tmp_path / "index.html"
    html.write_text('<img src="foo_bar.png" />', encoding="utf-8")
    assert check_underscores.main([str(tmp_path)]) == 1
    captured = capsys.readouterr()
    assert "foo_bar.png" in captured.err
