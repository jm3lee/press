from __future__ import annotations

from pathlib import Path

from pie.check import permalinks as check_permalinks


def test_duplicate_permalinks_fail(tmp_path: Path, monkeypatch) -> None:
    """Duplicate permalink values -> exit code 1."""
    src = tmp_path / "src"
    src.mkdir()
    (src / "a.md").write_text("---\npermalink: /dup\n---\n", encoding="utf-8")
    (src / "b.md").write_text("---\npermalink: /dup\n---\n", encoding="utf-8")
    monkeypatch.chdir(tmp_path)
    rc = check_permalinks.main(["-l", str(tmp_path / "log.txt")])
    assert rc == 1


def test_unique_permalinks_pass(tmp_path: Path, monkeypatch) -> None:
    """Unique or missing permalinks -> exit code 0 and log file created."""
    src = tmp_path / "src"
    src.mkdir()
    (src / "a.md").write_text("---\npermalink: /a\n---\n", encoding="utf-8")
    (src / "b.md").write_text("---\npermalink: /b\n---\n", encoding="utf-8")
    (src / "c.md").write_text("---\n---\n", encoding="utf-8")
    log = tmp_path / "log.txt"
    monkeypatch.chdir(tmp_path)
    rc = check_permalinks.main(["-l", str(log)])
    assert rc == 0
    assert log.exists()


def test_parse_args_defaults() -> None:
    """parse_args returns default options."""
    args = check_permalinks.parse_args([])
    assert args.directory == "src"
    assert args.log == "log/check-permalinks.txt"
