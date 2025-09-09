from pathlib import Path

from bs4 import BeautifulSoup
from jinja2 import Undefined
from pie.render import html

def _setup_template(tmp_path, monkeypatch):
    template = Path("/data/src/templates/template.html.jinja").read_text(
        encoding="utf-8"
    )
    tmpl_dir = tmp_path / "src" / "templates"
    tmpl_dir.mkdir(parents=True)
    (tmpl_dir / "template.html.jinja").write_text(template, encoding="utf-8")
    md = tmp_path / "page.md"
    md.write_text(
        "{% extends \"src/templates/template.html.jinja\" %}\n"
        "{% block body %}Body{% endblock %}\n",
        encoding="utf-8",
    )
    ctx = {
        "doc": {"title": "T", "link": {"canonical": ""}},
        "html": {"scripts": []},
    }
    monkeypatch.setenv("PIE_DATA_DIR", str(tmp_path))
    html.env = html.create_env()
    html.env.undefined = Undefined
    monkeypatch.chdir(tmp_path)
    return md.name, ctx


def test_mathjax_enabled_includes_script(tmp_path, monkeypatch):
    """doc.mathjax True -> MathJax script tag present."""
    md, ctx = _setup_template(tmp_path, monkeypatch)
    ctx["doc"]["mathjax"] = True
    rendered = html.render_page(md, ctx)
    soup = BeautifulSoup(rendered, "html.parser")
    assert soup.find("script", id="MathJax-script") is not None


def test_mathjax_disabled_omits_script(tmp_path, monkeypatch):
    """doc.mathjax False -> MathJax script tag absent."""
    md, ctx = _setup_template(tmp_path, monkeypatch)
    ctx["doc"]["mathjax"] = False
    rendered = html.render_page(md, ctx)
    soup = BeautifulSoup(rendered, "html.parser")
    assert soup.find("script", id="MathJax-script") is None


def test_mathjax_included_once(tmp_path, monkeypatch):
    """MathJax script appears once even after multiple renders."""
    md, ctx = _setup_template(tmp_path, monkeypatch)
    ctx["doc"]["mathjax"] = True
    html.render_page(md, ctx)
    rendered = html.render_page(md, ctx)
    soup = BeautifulSoup(rendered, "html.parser")
    assert len(soup.find_all("script", id="MathJax-script")) == 1
