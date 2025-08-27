from __future__ import annotations

from pathlib import Path

from pie.check import breadcrumbs as check_breadcrumbs


def test_main_reports_missing(tmp_path: Path, monkeypatch) -> None:
    """YAML without breadcrumbs -> exit code 1."""
    src = tmp_path / "src"
    src.mkdir()
    yml = src / "doc.yml"
    yml.write_text("title: Test\n", encoding="utf-8")
    md = src / "doc.md"
    md.write_text("---\ntitle: Test\n---\n", encoding="utf-8")
    yaml_file = src / "other.yaml"
    yaml_file.write_text("title: Other\n", encoding="utf-8")
    monkeypatch.chdir(tmp_path)
    rc = check_breadcrumbs.main(["-l", str(tmp_path / "log.txt")])
    assert rc == 1


def test_main_passes_and_logs(tmp_path: Path, monkeypatch) -> None:
    """YAML with breadcrumbs -> exit 0 and write log."""
    src = tmp_path / "src"
    src.mkdir()
    yml = src / "doc.yml"
    yml.write_text(
        "title: Test\nbreadcrumbs:\n  - title: Home\n",
        encoding="utf-8",
    )
    md = src / "doc.md"
    md.write_text(
        "---\ntitle: Test\nbreadcrumbs:\n  - title: Home\n---\n",
        encoding="utf-8",
    )
    yaml_file = src / "other.yaml"
    yaml_file.write_text(
        "title: Other\nbreadcrumbs:\n  - title: Home\n",
        encoding="utf-8",
    )
    log = tmp_path / "log.txt"
    monkeypatch.chdir(tmp_path)
    rc = check_breadcrumbs.main(["-l", str(log)])
    assert rc == 0
    assert log.exists()


def test_main_exclude(tmp_path: Path, monkeypatch) -> None:
    """exclude.yml skips failing file."""
    src = tmp_path / "src"
    src.mkdir()
    md = src / "doc.md"
    md.write_text("---\ntitle: Test\n---\n", encoding="utf-8")
    exclude = tmp_path / "exclude.yml"
    exclude.write_text("- doc.md\n", encoding="utf-8")
    monkeypatch.chdir(tmp_path)
    assert check_breadcrumbs.main(["-x", str(exclude)]) == 0


def test_parse_args_defaults() -> None:
    """parse_args returns default paths."""
    args = check_breadcrumbs.parse_args([])
    assert args.directory == "src"
    assert args.log == "log/check-breadcrumbs.txt"

