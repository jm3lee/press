import os

import fakeredis
import pytest
import ruamel.yaml as yaml
from pathlib import Path

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
    """Frontmatter {'title': 'T'} -> url/id/doc.citation added."""
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
    assert data["doc"]["citation"] == "t"
    assert data["doc"]["mathjax"] is False
    assert data["id"] == "doc"
    assert data["schema"] == "v1"


def test_read_from_yaml_generates_fields(tmp_path):
    """YAML {'title': 'Foo'} -> metadata with url/id/doc.citation."""
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
    assert data["doc"]["citation"] == "foo"
    assert data["doc"]["mathjax"] is False
    assert data["id"] == "item"
    assert data["schema"] == "v1"


def test_schema_default():
    """Schema dataclass defaults to current version."""
    from pie.schema import Schema

    assert Schema().schema == "v1"


def test_press_defaults_to_v2():
    """Press metadata enforces the ``v2`` schema version."""
    from pie.model import Press

    info = Press(id="doc")
    assert info.schema == "v2"


def test_press_invalid_schema_raises():
    """Attempting to override ``press.schema`` raises an error."""
    from pie.model import Press

    with pytest.raises(ValueError):
        Press(id="doc", schema="v1")


def test_metadata_v2_to_dict():
    """MetadataV2 serializes only ``press`` information."""
    from pie.model import MetadataV2, Press

    metadata_v2 = MetadataV2(press=Press(id="doc"))

    assert metadata_v2.to_dict() == {"press": {"id": "doc", "schema": "v2"}}


def test_metadata_v2_rejects_unknown_fields():
    """Passing unexpected fields raises a ``TypeError``."""
    from pie.model import MetadataV2, Press

    with pytest.raises(TypeError):
        MetadataV2(id="doc", press=Press(id="doc"))


def test_load_metadata_pair_conflict_shows_path(tmp_path, monkeypatch):
    """Conflicting values include path in warning."""
    md = tmp_path / "dir" / "post.md"
    md.parent.mkdir(parents=True)
    md.write_text("---\nurl: /md\n---\n")
    yml = md.with_suffix(".yml")
    yml.write_text("url: /yml\n")
    os.chdir(tmp_path)
    try:
        messages = []

        def fake_warning(msg, *args, **kwargs):
            messages.append(msg.format(*args))

        monkeypatch.setattr(metadata.logger, "warning", fake_warning)

        metadata.load_metadata_pair(yml)
        assert any("dir/post.yml" in m for m in messages)
    finally:
        os.chdir("/tmp")


def test_load_metadata_pair_accepts_mdi(tmp_path):
    """'.mdi' files are treated like '.md'."""
    mdi = tmp_path / "src" / "post.mdi"
    mdi.parent.mkdir(parents=True)
    mdi.write_text("---\ntitle: MDI\n---\n")
    os.chdir(tmp_path)
    try:
        data = metadata.load_metadata_pair(Path("src/post.mdi"))
    finally:
        os.chdir("/tmp")
    assert data["title"] == "MDI"
    assert data["path"] == ["src/post.mdi"]


def test_read_from_yaml_error_logs_path(tmp_path):
    """Malformed YAML reports the filename."""
    bad = tmp_path / "bad.yml"
    bad.write_text(":\n")
    os.chdir(tmp_path)
    try:
        with pytest.raises(yaml.YAMLError) as excinfo:
            metadata.read_from_yaml("bad.yml")
    finally:
        os.chdir("/tmp")
    assert "bad.yml" in str(excinfo.value)


def test_get_url_from_build_md(tmp_path):
    """'build/foo.md' -> '/foo.html'."""
    path = tmp_path / "build" / "foo.md"
    path.parent.mkdir(parents=True)
    path.write_text("")
    os.chdir(tmp_path)
    try:
        assert metadata.get_url("build/foo.md") == "/foo.html"
    finally:
        os.chdir("/tmp")


def test__add_citation_if_missing_from_name():
    """Deprecated 'name' populates 'doc.citation'."""
    info = {"name": "Example"}
    metadata._add_citation_if_missing(info, "doc.md")
    assert info["doc"]["citation"] == "example"


def test__add_canonical_link_if_missing_existing():
    """Existing canonical link is preserved."""
    info = {"doc": {"link": {"canonical": "/x"}}}
    metadata._add_canonical_link_if_missing(info, "doc.md")
    assert info["doc"]["link"]["canonical"] == "/x"


def test__add_canonical_link_if_missing_no_url():
    """No url leaves canonical link unset."""
    info: dict[str, str] = {}
    metadata._add_canonical_link_if_missing(info, "doc.md")
    assert "doc" not in info


def test__add_canonical_link_if_missing_sets_value(monkeypatch):
    """URL present populates ``doc.link.canonical`` using ``BASE_URL``."""
    monkeypatch.setenv("BASE_URL", "http://press.io")
    info = {"url": "/foo"}
    metadata._add_canonical_link_if_missing(info, "doc.md")
    assert info["doc"]["link"]["canonical"] == "http://press.io/foo"


def test__add_if_missing_nested_key():
    """Nested dotted keys are created when missing."""
    info: dict[str, str] = {}
    metadata._add_if_missing(info, "foo.bar", "baz", "doc.md")
    assert info["foo"]["bar"] == "baz"


def test__get_redis_value_missing_returns_none():
    """Missing Redis key returns None."""
    fake = fakeredis.FakeRedis(decode_responses=True)
    metadata.redis_conn = fake
    try:
        assert metadata._get_redis_value("nope") is None
    finally:
        metadata.redis_conn = None

