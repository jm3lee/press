from pie.render import html


def test_main_renders_file(tmp_path, monkeypatch):
    md = tmp_path / "page.md"
    md.write_text("---\n---\n{{ foo }}", encoding="utf-8")
    ctx = tmp_path / "ctx.yml"
    ctx.write_text("foo: bar", encoding="utf-8")
    out = tmp_path / "out.html"
    monkeypatch.setenv("PIE_DATA_DIR", str(tmp_path))
    html.env = html.create_env()
    monkeypatch.chdir(tmp_path)
    html.main(["page.md", "ctx.yml", "out.html"])
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
    monkeypatch.setenv("PIE_DATA_DIR", str(tmp_path))
    html.env = html.create_env()
    monkeypatch.chdir(tmp_path)
    html.main(["table.md", "ctx.yml", "out.html"])
    text = out.read_text(encoding="utf-8")
    assert "| 1 | 2 |" in text


def test_render_page_allows_raw_html(tmp_path, monkeypatch):
    md = tmp_path / "raw.md"
    md.write_text("---\n---\n<div>raw</div>", encoding="utf-8")
    monkeypatch.setenv("PIE_DATA_DIR", str(tmp_path))
    html.env = html.create_env()
    monkeypatch.chdir(tmp_path)
    rendered = html.render_page("raw.md")
    assert "<div>raw</div>" in rendered
