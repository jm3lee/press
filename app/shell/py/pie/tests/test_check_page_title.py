from __future__ import annotations

from pathlib import Path

from pie import check_page_title


def test_main_pass(tmp_path: Path) -> None:
    html = tmp_path / "index.html"
    html.write_text("<html><h1>Title</h1></html>", encoding="utf-8")
    assert check_page_title.main([str(tmp_path)]) == 0


def test_main_fail(tmp_path: Path, capsys) -> None:
    html = tmp_path / "index.html"
    html.write_text("<html></html>", encoding="utf-8")
    assert check_page_title.main([str(tmp_path)]) == 1
    captured = capsys.readouterr()
    assert "Missing or empty <h1>" in captured.out


def test_main_exclude(tmp_path: Path) -> None:
    html = tmp_path / "index.html"
    html.write_text("<html></html>", encoding="utf-8")
    exclude = tmp_path / "exclude.yml"
    exclude.write_text("- index.html\n", encoding="utf-8")
    assert check_page_title.main([str(tmp_path), "-x", str(exclude)]) == 0

