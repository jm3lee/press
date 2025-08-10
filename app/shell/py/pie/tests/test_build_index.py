import os
import json
from pathlib import Path
import pytest
from pie import build_index


def test_validate_and_insert_duplicate(tmp_path):
    """Duplicate id triggers KeyError."""
    index = {"a": {"id": "a"}}
    with pytest.raises(KeyError):
        build_index.validate_and_insert_metadata({"id": "a"}, "file", index)


def test_build_index_handles_multiple_extensions(tmp_path):
    """'.md' and '.yml' -> index with both entries."""
    src = tmp_path / "src"
    src.mkdir()
    md = src / "doc.md"
    md.write_text("---\n{\"title\": \"T\", \"id\": \"doc\"}\n---\n")
    yml = src / "item.yml"
    yml.write_text('{"title": "Foo"}')

    os.chdir(tmp_path)
    try:
        index = build_index.build_index("src")
    finally:
        os.chdir("/tmp")

    assert set(index) == {"doc", "item"}


def test_main_writes_log_file(tmp_path):
    """CLI writes index.json and build.log."""
    src = tmp_path / "src"
    src.mkdir()
    md = src / "doc.md"
    md.write_text("---\n{\"title\": \"T\", \"id\": \"doc\"}\n---\n")
    yml = src / "item.yml"
    yml.write_text('{"title": "Foo"}')
    out = tmp_path / "index.json"
    log = tmp_path / "build.log"

    os.chdir(tmp_path)
    try:
        build_index.main(["src", "-o", str(out), "--log", str(log)])
    finally:
        os.chdir("/tmp")

    assert out.exists()
    data = json.loads(out.read_text())
    assert set(data) == {"doc", "item"}
    assert log.exists()
