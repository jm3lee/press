import pytest
from pie import render_jinja_template as render_template


def test_get_desc_returns_metadata(monkeypatch):
    monkeypatch.setattr(render_template, "_get_metadata", lambda name: {"id": name})
    assert render_template.get_desc("entry") == {"id": "entry"}


def test_get_desc_missing_raises(monkeypatch):
    monkeypatch.setattr(render_template, "_get_metadata", lambda name: None)
    with pytest.raises(SystemExit):
        render_template.get_desc("entry")


def test_to_alpha_index_maps():
    assert [render_template.to_alpha_index(i) for i in range(4)] == list("abcd")


def test_read_yaml_yields_toc(tmp_path):
    yml = tmp_path / "t.yml"
    yml.write_text("toc:\n - 1\n - 2\n", encoding="utf-8")
    assert list(render_template.read_yaml(yml)) == [1, 2]


def test_extract_front_matter(tmp_path):
    md = tmp_path / "f.md"
    md.write_text("---\ntitle: Hi\n---\nbody\n", encoding="utf-8")
    assert render_template.extract_front_matter(md) == {"title": "Hi"}


def test_extract_front_matter_missing(tmp_path):
    md = tmp_path / "f.md"
    md.write_text("no front matter", encoding="utf-8")
    assert render_template.extract_front_matter(md) is None


def test_render_jinja_renders_snippet():
    render_template.index_json = {"name": "world"}
    assert render_template.render_jinja("Hello {{ name }}") == "Hello world"
