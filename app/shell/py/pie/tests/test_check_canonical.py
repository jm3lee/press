from __future__ import annotations

from pathlib import Path

from pie.check import canonical as check_canonical


def test_main_pass(tmp_path: Path) -> None:
    """Canonical link without localhost -> exit code 0."""
    html = tmp_path / "index.html"
    html.write_text(
        '<link rel="canonical" href="https://example.com/foo.html" />',
        encoding="utf-8",
    )
    assert check_canonical.main([str(tmp_path)]) == 0


def test_fail_localhost(tmp_path: Path, capsys) -> None:
    """Canonical link pointing to localhost -> exit code 1."""
    html = tmp_path / "index.html"
    html.write_text(
        '<link rel="canonical" href="http://localhost/foo.html" />',
        encoding="utf-8",
    )
    assert check_canonical.main([str(tmp_path)]) == 1
    captured = capsys.readouterr()
    assert "localhost" in captured.err
