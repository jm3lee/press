import json
import os
import sys
from pathlib import Path

import pytest

# Ensure packages are importable when tests run from the repository root
TEST_ROOT = Path(__file__).resolve()
sys.path.insert(0, str(TEST_ROOT.parents[1]))  # magicbar package
sys.path.insert(0, str(TEST_ROOT.parents[5] / "app/shell/py/pie"))
from magicbar import index


def test_scan_path_collects_metadata(tmp_path):
    src = tmp_path / "src"
    src.mkdir()
    (src / "alpha.yml").write_text("title: Alpha\nmagicbar:\n  shortcut: a\n", encoding="utf-8")
    (src / "beta.md").write_text("---\ntitle: Beta\n---\n", encoding="utf-8")

    os.chdir(tmp_path)
    try:
        entries = sorted(index.scan_path(Path("src")), key=lambda x: x["title"])
    finally:
        os.chdir("/tmp")
    assert entries == [
        {"title": "Alpha", "url": "/alpha.html", "shortcut": "a"},
        {"title": "Beta", "url": "/beta.html"},
    ]


def test_main_writes_default_output(tmp_path, monkeypatch, capsys):
    src = tmp_path / "src"
    src.mkdir()
    (src / "alpha.yml").write_text("title: Alpha\n", encoding="utf-8")

    os.chdir(tmp_path)
    monkeypatch.setattr(sys, "argv", ["magicbar-index", "src"])
    try:
        index.main()
    finally:
        os.chdir("/tmp")

    output_path = tmp_path / "magicbar.json"
    data = json.loads(output_path.read_text())
    assert data == [{"title": "Alpha", "url": "/alpha.html"}]
    captured = capsys.readouterr()
    assert captured.out == ""


def test_scan_path_merges_markdown_and_yaml(tmp_path):
    src = tmp_path / "src"
    src.mkdir()
    (src / "alpha.md").write_text("---\ntitle: FromMD\n---\n", encoding="utf-8")
    (src / "alpha.yml").write_text(
        "title: FromYAML\nmagicbar:\n  shortcut: a\n", encoding="utf-8"
    )
    os.chdir(tmp_path)
    try:
        entries = list(index.scan_path(Path("src")))
    finally:
        os.chdir("/tmp")
    assert entries == [{"title": "FromYAML", "url": "/alpha.html", "shortcut": "a"}]
