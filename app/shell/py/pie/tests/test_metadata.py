import os
import pytest

from pie import metadata


def test_get_url_from_src_md(tmp_path):
    """'src/foo.md' -> '/foo.html'."""
    path = tmp_path / "src" / "foo.md"
    path.parent.mkdir(parents=True)
    path.write_text("")
    os.chdir(tmp_path)
    try:
        assert metadata.get_url("src/foo.md") == "/foo.html"
    finally:
        os.chdir("/tmp")


def test_get_url_invalid_raises(tmp_path):
    """Unknown path raises an error."""
    bad = tmp_path / "foo.md"
    bad.write_text("")
    os.chdir(tmp_path)
    try:
        with pytest.raises(Exception):
            metadata.get_url("foo.md")
    finally:
        os.chdir("/tmp")


def test__read_from_markdown_generates_fields(tmp_path):
    """Frontmatter {'title': 'T'} -> url/id/citation added."""
    md = tmp_path / "src" / "doc.md"
    md.parent.mkdir(parents=True)
    md.write_text("---\n{\"title\": \"T\"}\n---\nbody")
    os.chdir(tmp_path)
    try:
        data = metadata._read_from_markdown("src/doc.md")
        assert data is not None
        data = metadata.generate_missing_metadata(data, "src/doc.md")
    finally:
        os.chdir("/tmp")
    assert data["title"] == "T"
    assert data["url"] == "/doc.html"
    assert data["citation"] == "t"
    assert data["id"] == "doc"


def test_read_from_yaml_generates_fields(tmp_path):
    """YAML {'title': 'Foo'} -> metadata with url/id/citation."""
    yml = tmp_path / "src" / "item.yml"
    yml.parent.mkdir(parents=True)
    yml.write_text('{"title": "Foo"}')
    os.chdir(tmp_path)
    try:
        data = metadata.read_from_yaml("src/item.yml")
        assert data is not None
        data = metadata.generate_missing_metadata(data, "src/item.yml")
    finally:
        os.chdir("/tmp")
    assert data["title"] == "Foo"
    assert data["url"] == "/item.html"
    assert data["citation"] == "foo"
    assert data["id"] == "item"


def test_load_metadata_pair_conflict_shows_path(tmp_path):
    """Conflicting values include path in warning."""
    md = tmp_path / "dir" / "post.md"
    md.parent.mkdir(parents=True)
    md.write_text("---\nurl: /md\n---\n")
    yml = md.with_suffix(".yml")
    yml.write_text("url: /yml\n")
    os.chdir(tmp_path)
    try:
        with pytest.warns(UserWarning) as record:
            metadata.load_metadata_pair(yml)
        assert "dir/post.yml" in str(record[0].message)
    finally:
        os.chdir("/tmp")

