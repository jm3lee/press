from pie.render import html


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
    html.main([str(md), str(out), "--template", "base.html", "--context", str(ctx)])
    assert "bar" in out.read_text(encoding="utf-8")


def test_main_renders_table(tmp_path, monkeypatch):
    md = tmp_path / "table.md"
    md.write_text(
        "---\n---\n| a | b |\n| --- | --- |\n| 1 | 2 |\n",
        encoding="utf-8",
    )
    tmpl = tmp_path / "base.html"
    tmpl.write_text("{{ content }}", encoding="utf-8")
    out = tmp_path / "out.html"
    monkeypatch.setenv("PIE_DATA_DIR", str(tmp_path))
    html.env = html.create_env()
    html.main([str(md), str(out), "--template", "base.html"])
    text = out.read_text(encoding="utf-8")
    assert "<table>" in text
    assert "<td>1</td>" in text
