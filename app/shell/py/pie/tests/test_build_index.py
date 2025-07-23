import os
import json
from pathlib import Path
import pytest

from pie import build_index


def test_get_url_from_src_md(tmp_path):
    path = tmp_path / "src" / "foo.md"
    path.parent.mkdir(parents=True)
    path.write_text("")
    os.chdir(tmp_path)
    try:
        assert build_index.get_url("src/foo.md") == "/foo.html"
    finally:
        os.chdir("/tmp")


def test_get_url_invalid_raises(tmp_path):
    bad = tmp_path / "foo.md"
    bad.write_text("")
    os.chdir(tmp_path)
    try:
        with pytest.raises(Exception):
            build_index.get_url("foo.md")
    finally:
        os.chdir("/tmp")


def test_process_markdown_parses_frontmatter(tmp_path):
    md = tmp_path / "src" / "doc.md"
    md.parent.mkdir(parents=True)
    md.write_text("---\n{\"title\": \"T\"}\n---\nbody")
    os.chdir(tmp_path)
    try:
        data = build_index.process_markdown("src/doc.md")
    finally:
        os.chdir("/tmp")
    assert data == {"title": "T", "url": "/doc.html"}


def test_process_yaml_generates_fields(tmp_path):
    yml = tmp_path / "src" / "item.yml"
    yml.parent.mkdir(parents=True)
    yml.write_text('{"name": "Foo"}')
    os.chdir(tmp_path)
    try:
        data = build_index.process_yaml("src/item.yml")
    finally:
        os.chdir("/tmp")
    assert data["name"] == "Foo"
    assert data["url"] == "/item.html"
    assert data["citation"] == "foo"
    assert data["id"] == "item"


def test_validate_and_insert_duplicate(tmp_path):
    index = {"a": {"id": "a"}}
    with pytest.raises(KeyError):
        build_index.validate_and_insert_metadata({"id": "a"}, "file", index)
