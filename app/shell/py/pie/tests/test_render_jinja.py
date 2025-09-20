
import json
import runpy
import sys
from pathlib import Path

import pytest
from jinja2 import FileSystemLoader, TemplateSyntaxError

from pie.render import jinja

def test_resolve_citation_pages_list():
    desc = {"doc": {"citation": {"author": "smith", "year": 1999, "page": [1, 2]}}}
    text, needs_parens = jinja._resolve_citation(desc, "citation")
    assert text == "Smith 1999, 1, 2"
    assert needs_parens is True

def test_render_link_invalid_descriptor_raises():
    with pytest.raises(SystemExit):
        jinja.render_link(123)  # type: ignore[arg-type]

def test_figure_urls_single_mapping_and_string():
    desc_map = {
        "title": "t",
        "url": "image.jpg",
        "figure": {"urls": {"url": "a.jpg", "width": 100}},
    }
    desc_str = {"title": "t", "url": "image.jpg", "figure": {"urls": "a.jpg"}}
    assert 'srcset="a.jpg 100w"' in jinja.figure(desc_map)
    assert 'srcset="a.jpg"' in jinja.figure(desc_str)

def test_figure_invalid_descriptor_raises():
    with pytest.raises(SystemExit):
        jinja.figure(123)  # type: ignore[arg-type]

def test_figure_widths_with_placeholder_in_url():
    desc = {
        "title": "t",
        "url": "img-{width}.jpg",
        "figure": {"widths": [100, 200]},
    }
    out = jinja.figure(desc)
    assert 'srcset="img-100.jpg 100w, img-200.jpg 200w"' in out

def test_figure_widths_regex_pattern_and_default_src():
    desc = {"title": "t", "url": "img-100.jpg", "figure": {"widths": [100, 200]}}
    out = jinja.figure(desc)
    assert 'img-200.jpg 200w' in out

    desc_no_src = {"title": "t", "figure": {"widths": [100], "pattern": "img-{width}.jpg"}}
    out_no_src = jinja.figure(desc_no_src)
    assert 'src="img-100.jpg"' in out_no_src

def test_definition_invalid_descriptor_raises():
    with pytest.raises(SystemExit):
        jinja.definition(123)  # type: ignore[arg-type]

def test_definition_missing_snippet_returns_empty():
    assert jinja.definition({}) == ""

def test_cite_with_simple_string_citation(monkeypatch):
    desc = {"doc": {"citation": "Simple"}, "url": "u", "title": "T"}

    def fake_get(name: str):
        return desc

    monkeypatch.setattr(jinja, "get_cached_metadata", fake_get)
    html = jinja.cite("ref")
    assert "Simple" in html

def test_parse_args_parses_values():
    args = jinja.parse_args([
        "tmpl", "out", "--index", "i.json", "--config", "cfg.yml"
    ])
    assert args.template == "tmpl"
    assert args.output == "out"
    assert args.index == "i.json"
    assert args.config == "cfg.yml"


def test_render_press_replaces_alias():
    html = jinja.render_press("Hi :smile:")
    assert str(html) == "<p>Hi 😄</p>\n"


def test_render_press_ignores_unknown_alias():
    html = jinja.render_press("Hi :does_not_exist:")
    assert str(html) == "<p>Hi :does_not_exist:</p>\n"


def test_render_press_renders_footnotes():
    text = "Note.[^1]\n\n[^1]: Footnote"
    html = jinja.render_press(text)
    assert '<section class="footnotes"' in str(html)

