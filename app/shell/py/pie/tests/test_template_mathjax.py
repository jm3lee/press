import importlib

from bs4 import BeautifulSoup
from jinja2 import Undefined


def _load_html(tmp_path, monkeypatch):
    monkeypatch.setenv("PIE_DATA_DIR", str(tmp_path))
    from pie.render import jinja as jinja_module

    importlib.reload(jinja_module)
    from pie.render import html as html_module

    importlib.reload(html_module)
    return html_module


def _setup_template(tmp_path, monkeypatch):
    template = tmp_path / "template.html.jinja"
    template.write_text(
        "{% if doc.mathjax %}"
        "<script id=\"MathJax-script\"></script>"
        "{% endif %}",
        encoding="utf-8",
    )
    (tmp_path / "macros.jinja").write_text(
        "{% macro anchor(id) %}{% endmacro %}",
        encoding="utf-8",
    )
    md = tmp_path / "page.md"
    md.write_text("---\n---\nBody", encoding="utf-8")
    ctx = {
        "doc": {"title": "T", "link": {"canonical": ""}},
        "html": {"scripts": []},
    }
    html = _load_html(tmp_path, monkeypatch)
    html.env = html.create_env()
    html.env.undefined = Undefined
    monkeypatch.chdir(tmp_path)
    return html, template.name, md.name, ctx


def test_mathjax_enabled_includes_script(tmp_path, monkeypatch):
    """doc.mathjax True -> MathJax script tag present."""
    html, template, md, ctx = _setup_template(tmp_path, monkeypatch)
    ctx["doc"]["mathjax"] = True
    rendered = html.render_page(template, md, ctx)
    soup = BeautifulSoup(rendered, "html.parser")
    assert soup.find("script", id="MathJax-script") is not None


def test_mathjax_disabled_omits_script(tmp_path, monkeypatch):
    """doc.mathjax False -> MathJax script tag absent."""
    html, template, md, ctx = _setup_template(tmp_path, monkeypatch)
    ctx["doc"]["mathjax"] = False
    rendered = html.render_page(template, md, ctx)
    soup = BeautifulSoup(rendered, "html.parser")
    assert soup.find("script", id="MathJax-script") is None


def test_mathjax_included_once(tmp_path, monkeypatch):
    """MathJax script appears once even after multiple renders."""
    html, template, md, ctx = _setup_template(tmp_path, monkeypatch)
    ctx["doc"]["mathjax"] = True
    html.render_page(template, md, ctx)
    rendered = html.render_page(template, md, ctx)
    soup = BeautifulSoup(rendered, "html.parser")
    assert len(soup.find_all("script", id="MathJax-script")) == 1
