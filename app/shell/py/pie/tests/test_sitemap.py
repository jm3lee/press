from pie import sitemap


def test_generates_urls_without_index_html(tmp_path):
    build = tmp_path / "build"
    build.mkdir()
    (build / "index.html").write_text("", encoding="utf-8")
    (build / "page.html").write_text("", encoding="utf-8")
    sub = build / "sub"
    sub.mkdir()
    (sub / "index.html").write_text("", encoding="utf-8")
    (sub / "other.html").write_text("", encoding="utf-8")

    sitemap.main([str(build), "http://example.com"])

    expected = [
        "<?xml version=\"1.0\" encoding=\"UTF-8\"?>",
        '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">',
        "  <url><loc>http://example.com/</loc></url>",
        "  <url><loc>http://example.com/page.html</loc></url>",
        "  <url><loc>http://example.com/sub/</loc></url>",
        "  <url><loc>http://example.com/sub/other.html</loc></url>",
        "</urlset>",
    ]
    content = (build / "sitemap.xml").read_text(encoding="utf-8").splitlines()
    assert content == expected


def test_reads_base_url_from_env(tmp_path, monkeypatch):
    build = tmp_path / "build"
    build.mkdir()
    (build / "page.html").write_text("", encoding="utf-8")

    monkeypatch.setenv("BASE_URL", "http://example.com")
    sitemap.main([str(build)])

    text = (build / "sitemap.xml").read_text(encoding="utf-8")
    assert "http://example.com/page.html" in text

