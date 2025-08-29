
import json
import runpy
import sys
from pathlib import Path

import pytest
from jinja2 import FileSystemLoader, TemplateSyntaxError

from pie.render import jinja

def test_resolve_citation_pages_list():
    desc = {"citation": {"author": "smith", "year": 1999, "page": [1, 2]}}
    text, needs_parens = jinja._resolve_citation(desc, "citation")
    assert text == "Smith 1999, 1, 2"
    assert needs_parens is True

def test_render_link_invalid_descriptor_raises():
    with pytest.raises(SystemExit):
        jinja.render_link(123)  # type: ignore[arg-type]

def test_figure_with_string_descriptor_and_urls_list(monkeypatch):
    data = {
        "title": "t",
        "url": "image.jpg",
        "figure": {"urls": [{"url": "a.jpg", "width": 100}, "b.jpg"]},
    }
    monkeypatch.setattr(jinja, "get_cached_metadata", lambda k: data)
    result = jinja.figure("id")
    assert 'srcset="a.jpg 100w, b.jpg"' in result

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
    desc = {"citation": "Simple", "url": "u", "title": "T"}

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

def test_main_renders_template(tmp_path, monkeypatch):
    tmpl = tmp_path / "tmpl.txt"
    tmpl.write_text("Hello {{ name }}", encoding="utf-8")
    index = tmp_path / "index.json"
    index.write_text(json.dumps({"name": "World"}), encoding="utf-8")
    out = tmp_path / "out.txt"
    monkeypatch.setenv("PIE_DATA_DIR", str(tmp_path))
    jinja.env = jinja.create_env()
    jinja.main(["tmpl.txt", str(out), "--index", str(index)])
    assert out.read_text(encoding="utf-8") == "Hello World"

def test_entry_point_executes_main(tmp_path, monkeypatch):
    data_dir = tmp_path / "data"
    data_dir.mkdir()
    tmpl = data_dir / "tmpl.txt"
    tmpl.write_text("Hi {{ name }}", encoding="utf-8")
    index = tmp_path / "index.json"
    index.write_text(json.dumps({"name": "Agent"}), encoding="utf-8")
    out = tmp_path / "out.txt"
    script = Path(__file__).resolve().parent.parent / "pie" / "render" / "jinja.py"
    monkeypatch.setenv("PIE_DATA_DIR", str(data_dir))
    monkeypatch.setattr(
        sys,
        "argv",
        ["jinja.py", "tmpl.txt", str(out), "--index", str(index)],
        raising=False,
    )
    runpy.run_path(str(script), run_name="__main__")
    assert out.read_text(encoding="utf-8") == "Hi Agent"


def test_render_jinja_logs_template_syntax_error(monkeypatch):
    messages: list[str] = []
    handle = jinja.logger.add(messages.append, level="ERROR")
    try:
        with pytest.raises(TemplateSyntaxError):
            jinja.render_jinja("{{ oops")
    finally:
        jinja.logger.remove(handle)
    assert any("Template syntax error on line 1" in m for m in messages)
    assert any("{{ oops" in m for m in messages)


def test_render_jinja_logs_non_string_snippet(monkeypatch):
    messages: list[str] = []
    handle = jinja.logger.add(messages.append, level="ERROR")
    try:
        with pytest.raises(TypeError):
            jinja.render_jinja({"a": 1})
    finally:
        jinja.logger.remove(handle)
    assert any("Non-string snippet of type dict" in m for m in messages)
