
from pie.render import html


def test_render_page_converts_markdown_and_merges_metadata(tmp_path, monkeypatch):
    md = tmp_path / "page.md"
    md.write_text(
        "---\ntitle: Sample\n---\n\n# Heading\n\nBody text.", encoding="utf-8"
    )
    tmpl = tmp_path / "base.html"
    tmpl.write_text(
        "<title>{{ title }}</title>{{ content }}{{ extra }}", encoding="utf-8"
    )
    monkeypatch.setenv("PIE_DATA_DIR", str(tmp_path))
    html.env = html.create_env()
    result = html.render_page(md, "base.html", {"extra": "X"})
    assert "<h1 id=\"heading\">Heading</h1>" in result
    assert "<title>Sample</title>" in result
    assert "X" in result


def test_main_renders_file(tmp_path, monkeypatch):
    md = tmp_path / "page.md"
    md.write_text("---\n---\nHi", encoding="utf-8")
    tmpl = tmp_path / "base.html"
    tmpl.write_text("{{ content }}{{ foo }}", encoding="utf-8")
    ctx = tmp_path / "ctx.yml"
    ctx.write_text("foo: bar", encoding="utf-8")
    out = tmp_path / "out.html"
    monkeypatch.setenv("PIE_DATA_DIR", str(tmp_path))
    html.env = html.create_env()
    html.main([str(md), "base.html", str(out), "--context", str(ctx)])
    assert "bar" in out.read_text(encoding="utf-8")
