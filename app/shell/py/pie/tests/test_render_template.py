import pytest
import fakeredis
from pie import render_jinja_template as render_template


def test_default_class():
    desc = {"citation": "foo", "url": "/f"}
    html = render_template.render_link(desc, style="title")
    assert 'class="internal-link"' in html


def test_override_class():
    """link.class overrides default."""
    desc = {"citation": "foo", "url": "/f", "link": {"class": "external"}}
    html = render_template.render_link(desc, style="title")
    assert 'class="external"' in html


def test_tracking_false_adds_attributes():
    """tracking False -> rel/target attrs."""
    desc = {"link": {"tracking": False}}
    opts = render_template.get_tracking_options(desc)
    assert opts == 'rel="noopener noreferrer" target="_blank"'


def test_tracking_true_returns_empty():
    """tracking True -> no extra attrs."""
    desc = {"link": {"tracking": True}}
    opts = render_template.get_tracking_options(desc)
    assert opts == ""


def test_no_link_returns_empty():
    """No link section -> empty options."""
    desc = {"citation": "foo"}
    opts = render_template.get_tracking_options(desc)
    assert opts == ""


def test_missing_tracking_interpreted_as_false():
    """Absent tracking treated as False."""
    desc = {"link": {}}
    opts = render_template.get_tracking_options(desc)
    assert opts == 'rel="noopener noreferrer" target="_blank"'


def test_linktitle_uses_redis(monkeypatch):
    """Redis provides citation and url."""
    fake = fakeredis.FakeRedis(decode_responses=True)
    fake.set("item.citation", "Item")
    fake.set("item.url", "/i")
    monkeypatch.setattr(render_template, "redis_conn", fake)
    render_template.index_json = {}

    html = render_template.render_link("item", style="title")
    assert '<a href="/i"' in html
    assert ">Item<" in html


def test_linktitle_missing_raises(monkeypatch):
    """Unknown key -> SystemExit."""
    fake = fakeredis.FakeRedis(decode_responses=True)
    monkeypatch.setattr(render_template, "redis_conn", fake)
    render_template.index_json = {}

    with pytest.raises(SystemExit):
        render_template.render_link("foo", style="title")


def test_linktitle_skips_small_words():
    """Title style capitalizes but skips small words."""
    desc = {"citation": "movement in a circle", "url": "/c"}
    html = render_template.render_link(desc, style="title")
    assert ">Movement in a Circle<" in html


def test_link_uses_redis_tracking_and_ignores_icon(monkeypatch):
    """Redis data with tracking adds attrs, icon skipped."""
    fake = fakeredis.FakeRedis(decode_responses=True)
    fake.set("entry.citation", "link text")
    fake.set("entry.url", "/link")
    fake.set("entry.icon", "ICON")
    fake.set("entry.link.tracking", "false")
    monkeypatch.setattr(render_template, "redis_conn", fake)
    render_template.index_json = {}

    html = render_template.render_link("entry", use_icon=False)
    assert '<a href="/link"' in html
    assert 'link text' in html
    assert 'ICON' not in html
    assert 'rel="noopener noreferrer" target="_blank"' in html


def test_linkcap_includes_icon_and_capitalizes(monkeypatch):
    """style='cap' prepends icon and capitalizes first word."""
    fake = fakeredis.FakeRedis(decode_responses=True)
    fake.set("entry.citation", "foo bar")
    fake.set("entry.url", "/link")
    fake.set("entry.icon", "ICON")
    fake.set("entry.link.tracking", "false")
    monkeypatch.setattr(render_template, "redis_conn", fake)
    render_template.index_json = {}

    html = render_template.render_link("entry", style="cap")
    assert 'ICON Foo bar' in html
    assert 'Foo Bar' not in html
    assert 'rel="noopener noreferrer" target="_blank"' in html


def test_linkicon_includes_icon_without_capitalization(monkeypatch):
    """Default style shows icon; citation unchanged."""
    fake = fakeredis.FakeRedis(decode_responses=True)
    fake.set("entry.citation", "foo bar")
    fake.set("entry.url", "/link")
    fake.set("entry.icon", "ICON")
    fake.set("entry.link.tracking", "false")
    monkeypatch.setattr(render_template, "redis_conn", fake)
    render_template.index_json = {}

    html = render_template.render_link("entry")
    assert 'ICON foo bar' in html
    assert 'Foo bar' not in html
    assert 'rel="noopener noreferrer" target="_blank"' in html


def test_link_icon_title_capitalizes_each_word_and_includes_icon(monkeypatch):
    """style='title' capitalizes all words and shows icon."""
    fake = fakeredis.FakeRedis(decode_responses=True)
    fake.set("entry.citation", "foo bar")
    fake.set("entry.url", "/link")
    fake.set("entry.icon", "ICON")
    fake.set("entry.link.tracking", "false")
    monkeypatch.setattr(render_template, "redis_conn", fake)
    render_template.index_json = {}

    html = render_template.render_link("entry", style="title")
    assert 'ICON Foo Bar' in html
    assert 'rel="noopener noreferrer" target="_blank"' in html


def test_linkshort_uses_short_citation_and_ignores_icon(monkeypatch):
    """citation='short' uses short text without icon."""
    fake = fakeredis.FakeRedis(decode_responses=True)
    fake.set("entry.citation.short", "Short")
    fake.set("entry.url", "/link")
    fake.set("entry.icon", "ICON")
    fake.set("entry.link.tracking", "false")
    monkeypatch.setattr(render_template, "redis_conn", fake)
    render_template.index_json = {}

    html = render_template.render_link("entry", citation="short", use_icon=False)
    assert '>Short<' in html
    assert 'ICON' not in html
    assert 'rel="noopener noreferrer" target="_blank"' in html


def test_render_link_with_anchor():
    """anchor='bar' -> href endswith '#bar'."""
    desc = {"citation": "foo", "url": "/f"}
    html = render_template.render_link(desc, anchor="bar")
    assert '<a href="/f#bar"' in html


def test_wrapper_accepts_anchor(monkeypatch):
    """link() adds anchor to href."""
    fake = fakeredis.FakeRedis(decode_responses=True)
    fake.set("entry.citation", "Foo")
    fake.set("entry.url", "/link")
    monkeypatch.setattr(render_template, "redis_conn", fake)
    render_template.index_json = {}

    html = render_template.link("entry", anchor="top")
    assert '<a href="/link#top"' in html

