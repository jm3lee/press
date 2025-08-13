from __future__ import annotations

from pathlib import Path

from pie.check import author as check_author


def test_main_reports_missing(tmp_path: Path, monkeypatch) -> None:
    """YAML without author -> exit code 1."""
    src = tmp_path / "src"
    src.mkdir()
    yml = src / "doc.yml"
    yml.write_text("title: Test\n", encoding="utf-8")
    md = src / "doc.md"
    md.write_text("---\ntitle: Test\n---\n", encoding="utf-8")
    yaml_file = src / "other.yaml"
    yaml_file.write_text("title: Other\n", encoding="utf-8")
    monkeypatch.chdir(tmp_path)
    rc = check_author.main(["-l", str(tmp_path / "log.txt")])
    assert rc == 1


def test_main_passes_and_logs(tmp_path: Path, monkeypatch) -> None:
    """YAML with author -> exit 0 and write log."""
    src = tmp_path / "src"
    src.mkdir()
    yml = src / "doc.yml"
    yml.write_text("title: Test\nauthor: Jane Doe\n", encoding="utf-8")
    md = src / "doc.md"
    md.write_text("---\ntitle: Test\nauthor: Jane Doe\n---\n", encoding="utf-8")
    yaml_file = src / "other.yaml"
    yaml_file.write_text("title: Other\nauthor: Jane Doe\n", encoding="utf-8")
    log = tmp_path / "log.txt"
    monkeypatch.chdir(tmp_path)
    rc = check_author.main(["-l", str(log)])
    assert rc == 0
    assert log.exists()


def test_parse_args_defaults() -> None:
    """parse_args returns default paths."""
    args = check_author.parse_args([])
    assert args.directory == "src"
    assert args.log == "log/check-author.txt"
