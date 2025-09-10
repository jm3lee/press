import os
from pathlib import Path

import fakeredis
import pytest

from pie.render import jinja as render_template
from pie import metadata


def test_get_redis_value_initialises(monkeypatch):
    """Missing redis_conn -> initialised from env."""
    fake = fakeredis.FakeRedis(decode_responses=True)
    monkeypatch.setenv("REDIS_HOST", "h")
    monkeypatch.setenv("REDIS_PORT", "1234")
    monkeypatch.setattr(metadata, "redis_conn", None)
    monkeypatch.setattr(
        metadata.redis, "Redis", lambda host, port, decode_responses: fake
    )
    fake.set("foo", '"bar"')
    assert metadata._get_redis_value("foo") == "bar"


def test_get_redis_value_required_missing(monkeypatch):
    """required=True and missing key -> SystemExit."""
    fake = fakeredis.FakeRedis(decode_responses=True)
    monkeypatch.setattr(metadata, "redis_conn", fake)
    with pytest.raises(SystemExit):
        metadata._get_redis_value("missing", required=True)


def test_get_redis_value_error(monkeypatch):
    """Redis get() error -> SystemExit."""
    class Bad:
        def get(self, key):
            raise RuntimeError("boom")

    monkeypatch.setattr(metadata, "redis_conn", Bad())
    with pytest.raises(SystemExit):
        metadata._get_redis_value("foo")


def test_build_from_redis_initialises(monkeypatch):
    """_build_from_redis lazy-loads connection."""
    fake = fakeredis.FakeRedis(decode_responses=True)
    fake.set("entry.doc.citation", '"Foo"')
    fake.set("entry.url", '"/foo"')
    monkeypatch.setattr(metadata, "redis_conn", None)
    monkeypatch.setattr(
        metadata.redis, "Redis", lambda host, port, decode_responses: fake
    )
    assert metadata.build_from_redis("entry.") == {
        "doc": {"citation": "Foo"},
        "url": "/foo",
    }


def test_convert_lists():
    """Nested dict with numeric keys -> lists."""
    obj = {"0": {"0": "x", "1": "y"}, "1": [{"0": "z"}]}
    assert metadata._convert_lists(obj) == [["x", "y"], [["z"]]]


def test_get_cached_metadata_caches(monkeypatch):
    """Second lookup uses cached value."""
    calls: list[str] = []

    def fake_get(key):
        calls.append(key)
        return {"id": key}

    monkeypatch.setattr(render_template, "_get_metadata", fake_get)
    monkeypatch.setattr(render_template, "_metadata_cache", {})
    assert render_template.get_cached_metadata("x") == {"id": "x"}
    assert render_template.get_cached_metadata("x") == {"id": "x"}
    assert calls == ["x"]


def test_render_link_uses_citation_dict():
    """citation dict with 'alt' renders that text."""
    desc = {"doc": {"citation": {"citation": "Foo", "alt": "Alt"}}, "url": "/f"}
    html = render_template.render_link(desc, citation="alt", use_icon=False)
    assert ">Alt<" in html


def test_render_link_handles_citation_metadata():
    """citation with author/year/page formats like cite."""
    desc = {"doc": {"citation": {"author": "hull", "year": "2016", "page": "307"}}, "url": "/h"}
    html = render_template.render_link(desc, use_icon=False)
    assert ">(Hull 2016, 307)<" in html


def test_wrapper_functions():
    """Wrapper helpers render variants of links."""
    desc = {"doc": {"citation": "foo bar"}, "url": "/f", "icon": "I"}
    assert "Foo Bar" in render_template.linktitle(desc)
    assert "I Foo Bar" in render_template.link_icon_title(desc)
    assert "Foo bar" in render_template.linkcap(desc)
    assert "I foo bar" in render_template.linkicon(desc)
    short_desc = {"doc": {"citation": {"short": "S"}}, "url": "/s", "icon": "I"}
    html = render_template.linkshort(short_desc)
    assert ">S<" in html and "I" not in html


@pytest.mark.parametrize(
    "func, expected",
    [
        (render_template.linktitle, "Custom Citation"),
        (render_template.link_icon_title, "Custom Citation"),
        (render_template.linkcap, "Custom citation"),
        (render_template.linkicon, "custom citation"),
        (render_template.link, "custom citation"),
        (render_template.linkshort, "custom citation"),
    ],
)
def test_wrapper_functions_override_citation(func, expected):
    desc = {"doc": {"citation": "ignored"}, "url": "/f", "icon": "I"}
    html = func(desc, citation="custom citation")
    assert expected in html
    assert "ignored" not in html


def test_extract_front_matter_invalid_yaml(tmp_path):
    """Bad YAML front matter -> None."""
    md = tmp_path / "f.md"
    md.write_text("---\n: bad\n---\n", encoding="utf-8")
    assert render_template.extract_front_matter(md) is None


def test_process_directory(monkeypatch, tmp_path):
    """process_directory logs good titles and warns on bad files."""
    good = tmp_path / "good.md"
    good.write_text("---\ntitle: T\n---\n", encoding="utf-8")
    bad = tmp_path / "bad.md"
    bad.write_text("no front matter", encoding="utf-8")
    other = tmp_path / "skip.txt"
    other.write_text("irrelevant", encoding="utf-8")

    infos: list[tuple[str, dict]] = []
    warns: list[tuple[str, dict]] = []
    monkeypatch.setattr(
        render_template.logger, "info", lambda msg, **kw: infos.append((msg, kw))
    )
    monkeypatch.setattr(
        render_template.logger,
        "warning",
        lambda msg, **kw: warns.append((msg, kw)),
    )

    render_template.process_directory(tmp_path)

    assert any("TITLE:" in msg for msg, _ in infos)
    assert warns


def test_load_config_default_missing():
    """No config file -> empty dict."""
    assert render_template.load_config() == {}


def test_load_config_missing_custom(tmp_path):
    """Missing custom config -> SystemExit."""
    with pytest.raises(SystemExit):
        render_template.load_config(tmp_path / "missing.yml")


def test_load_config_invalid_yaml(tmp_path):
    """Invalid YAML raises SystemExit."""
    cfg = tmp_path / "c.yml"
    cfg.write_text(": bad\n", encoding="utf-8")
    with pytest.raises(SystemExit):
        render_template.load_config(cfg)


def test_load_config_valid(tmp_path):
    """Valid YAML returns dict."""
    cfg = tmp_path / "c.yml"
    cfg.write_text("a: 1\n", encoding="utf-8")
    assert render_template.load_config(cfg) == {"a": 1}
