import importlib


def _load_html(tmp_path, monkeypatch):
    monkeypatch.setenv("PIE_DATA_DIR", str(tmp_path))
    from pie.render import jinja as jinja_module

    importlib.reload(jinja_module)
    from pie.render import html as html_module

    importlib.reload(html_module)
    return html_module


def _write_template(tmp_path):
    template = tmp_path / "template.html.jinja"
    template.write_text(
        "{% filter press %}{% include markdown_path with context %}{% endfilter %}",
        encoding="utf-8",
    )
    (tmp_path / "macros.jinja").write_text(
        "{% macro anchor(id) %}{% endmacro %}",
        encoding="utf-8",
    )
    return template


def test_main_renders_file(tmp_path, monkeypatch):
    md = tmp_path / "page.md"
    md.write_text("---\n---\n{{ foo }}", encoding="utf-8")
    ctx = tmp_path / "ctx.yml"
    ctx.write_text("foo: bar", encoding="utf-8")
    out = tmp_path / "out.html"
    template = _write_template(tmp_path)
    html = _load_html(tmp_path, monkeypatch)
    html.env = html.create_env()
    monkeypatch.chdir(tmp_path)
    html.main([template.name, "page.md", "ctx.yml", "out.html"])
    assert "bar" in out.read_text(encoding="utf-8")


def test_main_renders_table(tmp_path, monkeypatch):
    md = tmp_path / "table.md"
    md.write_text(
        "---\n---\n| a | b |\n| --- | --- |\n| 1 | 2 |\n",
        encoding="utf-8",
    )
    ctx = tmp_path / "ctx.yml"
    ctx.write_text("", encoding="utf-8")
    out = tmp_path / "out.html"
    template = _write_template(tmp_path)
    html = _load_html(tmp_path, monkeypatch)
    html.env = html.create_env()
    monkeypatch.chdir(tmp_path)
    html.main([template.name, "table.md", "ctx.yml", "out.html"])
    text = out.read_text(encoding="utf-8")
    assert "<td>1</td>" in text


def test_render_page_allows_raw_html(tmp_path, monkeypatch):
    md = tmp_path / "raw.md"
    md.write_text("---\n---\n<div>raw</div>", encoding="utf-8")
    template = _write_template(tmp_path)
    html = _load_html(tmp_path, monkeypatch)
    html.env = html.create_env()
    monkeypatch.chdir(tmp_path)
    rendered = html.render_page(template.name, "raw.md")
    assert "<div>raw</div>" in rendered
