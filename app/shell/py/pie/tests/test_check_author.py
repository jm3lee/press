from __future__ import annotations
from pathlib import Path
import runpy
import sys

import pytest

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


def test_iter_metadata_handles_non_files(tmp_path: Path, monkeypatch) -> None:
    """``_iter_metadata`` skips directories and falls back to absolute paths."""

    root = tmp_path / "scan"
    root.mkdir()
    (root / "fake.md").mkdir()
    doc = root / "doc.md"
    doc.write_text("---\n---\n", encoding="utf-8")

    seen: list[Path] = []

    def fake_load(source: Path) -> None:
        seen.append(source)
        return None

    monkeypatch.setattr(check_author, "load_metadata_pair", fake_load)

    results = list(check_author._iter_metadata(root, tmp_path / "other"))

    assert seen == [doc]
    assert results == [(doc, [doc], None)]


def test_iter_metadata_resolves_absolute_paths(tmp_path: Path, monkeypatch) -> None:
    """Absolute ``meta['path']`` entries are resolved without modification."""

    root = tmp_path / "scan"
    root.mkdir()
    doc = root / "doc.md"
    doc.write_text("---\n---\n", encoding="utf-8")
    outside = tmp_path / "outside.yml"
    outside.write_text("title: Outside\n", encoding="utf-8")

    def fake_load(_: Path) -> dict:
        return {"path": [str(outside)], "doc": {"author": "Alice"}}

    monkeypatch.setattr(check_author, "load_metadata_pair", fake_load)

    [(metadata_path, paths, meta)] = list(
        check_author._iter_metadata(root, tmp_path)
    )

    assert metadata_path == doc
    assert paths == [outside.resolve()]
    assert meta["doc"]["author"] == "Alice"


def test_main_uses_default_exclude_file(tmp_path: Path, monkeypatch) -> None:
    """The default exclude file is honoured when present."""

    monkeypatch.chdir(tmp_path)
    src = tmp_path / "src"
    src.mkdir()
    doc = src / "doc.md"
    doc.write_text("---\ntitle: Sample\n---\n", encoding="utf-8")

    cfg = tmp_path / "cfg"
    cfg.mkdir()
    default_exclude = cfg / "check-author-exclude.yml"
    default_exclude.write_text("- doc.md\n", encoding="utf-8")

    def fake_iter(root: Path, base_dir: Path):
        yield doc, [doc], {"doc": {}}

    monkeypatch.setattr(check_author, "_iter_metadata", fake_iter)

    rc = check_author.main([])
    assert rc == 0


def test_main_skips_absolute_paths(tmp_path: Path, monkeypatch) -> None:
    """Paths outside the scan root are skipped when excluded explicitly."""

    src = tmp_path / "src"
    src.mkdir()
    doc = src / "doc.md"
    doc.write_text("---\ntitle: Sample\n---\n", encoding="utf-8")
    outside = tmp_path / "outside.md"
    outside.write_text("---\ntitle: Outside\n---\n", encoding="utf-8")

    def fake_iter(root: Path, base_dir: Path):
        yield doc, [outside], {"doc": {"author": "Jane"}}

    monkeypatch.setattr(check_author, "_iter_metadata", fake_iter)

    exclude = tmp_path / "exclude.yml"
    exclude.write_text(f"- {outside}\n", encoding="utf-8")

    monkeypatch.chdir(tmp_path)
    rc = check_author.main(["--exclude", str(exclude)])
    assert rc == 0


def test_entry_point_invokes_main(tmp_path: Path, monkeypatch) -> None:
    """Running the module as a script exits with ``SystemExit``."""

    monkeypatch.chdir(tmp_path)
    (tmp_path / "src").mkdir()
    monkeypatch.setattr(sys, "argv", ["author.py"], raising=False)

    with pytest.raises(SystemExit) as exc:
        runpy.run_path(str(Path(check_author.__file__)), run_name="__main__")

    assert exc.value.code == 0
