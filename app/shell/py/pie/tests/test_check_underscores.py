from __future__ import annotations

from pathlib import Path

from pie.check import underscores as check_underscores


def test_main_pass(tmp_path: Path) -> None:
    """URL without underscore -> exit code 0."""
    html = tmp_path / "index.html"
    html.write_text('<a href="foo-bar.html">link</a>', encoding="utf-8")
    assert check_underscores.main([str(tmp_path)]) == 0


def test_warn_href(tmp_path: Path, capsys) -> None:
    """URL with underscore -> exit code 0 with warning."""
    html = tmp_path / "index.html"
    html.write_text('<a href="foo_bar.html">link</a>', encoding="utf-8")
    assert check_underscores.main([str(tmp_path)]) == 0
    captured = capsys.readouterr()
    assert "foo_bar.html" in captured.err
    assert "dashes" in captured.err


def test_warn_src(tmp_path: Path, capsys) -> None:
    """Underscore in ``src`` attribute is reported."""
    html = tmp_path / "index.html"
    html.write_text('<img src="foo_bar.png" />', encoding="utf-8")
    assert check_underscores.main([str(tmp_path)]) == 0
    captured = capsys.readouterr()
    assert "foo_bar.png" in captured.err


def test_error_flag(tmp_path: Path) -> None:
    """`--error` exits with status 1 when underscores are present."""
    html = tmp_path / "index.html"
    html.write_text('<a href="foo_bar.html">link</a>', encoding="utf-8")
    assert check_underscores.main(["--error", str(tmp_path)]) == 1
