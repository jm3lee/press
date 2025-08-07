import os
from pathlib import Path

import fakeredis
import pytest

from pie import render_jinja_template as render_template


def test_get_redis_value_initialises(monkeypatch):
    fake = fakeredis.FakeRedis(decode_responses=True)
    monkeypatch.setenv("REDIS_HOST", "h")
    monkeypatch.setenv("REDIS_PORT", "1234")
    monkeypatch.setattr(render_template, "redis_conn", None)
    monkeypatch.setattr(
        render_template.redis, "Redis", lambda host, port, decode_responses: fake
    )
    fake.set("foo", '"bar"')
    assert render_template._get_redis_value("foo") == "bar"


def test_get_redis_value_required_missing(monkeypatch):
    fake = fakeredis.FakeRedis(decode_responses=True)
    monkeypatch.setattr(render_template, "redis_conn", fake)
    with pytest.raises(SystemExit):
        render_template._get_redis_value("missing", required=True)


def test_get_redis_value_error(monkeypatch):
    class Bad:
        def get(self, key):
            raise RuntimeError("boom")

    monkeypatch.setattr(render_template, "redis_conn", Bad())
    with pytest.raises(SystemExit):
        render_template._get_redis_value("foo")


def test_build_from_redis_initialises(monkeypatch):
    fake = fakeredis.FakeRedis(decode_responses=True)
    fake.set("entry.citation", '"Foo"')
    fake.set("entry.url", '"/foo"')
    monkeypatch.setattr(render_template, "redis_conn", None)
    monkeypatch.setattr(
        render_template.redis, "Redis", lambda host, port, decode_responses: fake
    )
    assert render_template._build_from_redis("entry.") == {
        "citation": "Foo",
        "url": "/foo",
    }


def test_convert_lists():
    obj = {"0": {"0": "x", "1": "y"}, "1": [{"0": "z"}]}
    assert render_template._convert_lists(obj) == [["x", "y"], [["z"]]]


def test_load_desc_invalid_type():
    with pytest.raises(SystemExit):
        render_template._load_desc(123)


def test_render_link_uses_citation_dict():
    desc = {"citation": {"citation": "Foo", "alt": "Alt"}, "url": "/f"}
    html = render_template.render_link(desc, citation="alt", use_icon=False)
    assert ">Alt<" in html


def test_wrapper_functions():
    desc = {"citation": "foo bar", "url": "/f", "icon": "I"}
    assert "Foo Bar" in render_template.linktitle(desc)
    assert "I Foo Bar" in render_template.link_icon_title(desc)
    assert "Foo bar" in render_template.linkcap(desc)
    assert "I foo bar" in render_template.linkicon(desc)
    short_desc = {"citation": {"short": "S"}, "url": "/s", "icon": "I"}
    html = render_template.linkshort(short_desc)
    assert ">S<" in html and "I" not in html


def test_extract_front_matter_invalid_yaml(tmp_path):
    md = tmp_path / "f.md"
    md.write_text("---\n: bad\n---\n", encoding="utf-8")
    assert render_template.extract_front_matter(md) is None


def test_process_directory(monkeypatch, tmp_path):
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
    assert render_template.load_config() == {}


def test_load_config_missing_custom(tmp_path):
    with pytest.raises(SystemExit):
        render_template.load_config(tmp_path / "missing.yml")


def test_load_config_invalid_yaml(tmp_path):
    cfg = tmp_path / "c.yml"
    cfg.write_text(": bad\n", encoding="utf-8")
    with pytest.raises(SystemExit):
        render_template.load_config(cfg)


def test_load_config_valid(tmp_path):
    cfg = tmp_path / "c.yml"
    cfg.write_text("a: 1\n", encoding="utf-8")
    assert render_template.load_config(cfg) == {"a": 1}
