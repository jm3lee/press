from __future__ import annotations

from pathlib import Path

from pie.check import author as check_author


def test_main_reports_missing(tmp_path: Path, monkeypatch) -> None:
    """YAML without doc.author -> exit code 1."""
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
    """YAML with doc.author -> exit 0 and write log."""
    src = tmp_path / "src"
    src.mkdir()
    yml = src / "doc.yml"
    yml.write_text("title: Test\ndoc:\n  author: Jane Doe\n", encoding="utf-8")
    md = src / "doc.md"
    md.write_text(
        "---\ntitle: Test\ndoc:\n  author: Jane Doe\n---\n",
        encoding="utf-8",
    )
    yaml_file = src / "other.yaml"
    yaml_file.write_text(
        "title: Other\ndoc:\n  author: Jane Doe\n", encoding="utf-8"
    )
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
    assert args.exclude is None


def test_parse_args_accepts_exclude_file() -> None:
    """``--exclude`` stores the provided filename."""

    args = check_author.parse_args(["--exclude", "foo.yml"])
    assert args.exclude == "foo.yml"


def test_main_skips_excluded_paths(tmp_path: Path, monkeypatch) -> None:
    """Files under excluded directories do not trigger failures."""

    src = tmp_path / "src"
    skip = src / "skip"
    keep = src / "keep"
    skip.mkdir(parents=True)
    keep.mkdir()

    (skip / "doc.yml").write_text("title: Test\n", encoding="utf-8")
    (skip / "doc.md").write_text("---\ntitle: Test\n---\n", encoding="utf-8")

    (keep / "doc.yml").write_text(
        "title: Other\ndoc:\n  author: Jane Doe\n",
        encoding="utf-8",
    )
    (keep / "doc.md").write_text(
        "---\ntitle: Other\ndoc:\n  author: Jane Doe\n---\n",
        encoding="utf-8",
    )

    monkeypatch.chdir(tmp_path)
    exclude = tmp_path / "exclude.yml"
    exclude.write_text("- skip/*\n", encoding="utf-8")

    rc = check_author.main(["--exclude", str(exclude)])
    assert rc == 0
