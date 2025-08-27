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


def test_excludes_paths(tmp_path):
    build = tmp_path / "build"
    build.mkdir()
    (build / "keep.html").write_text("", encoding="utf-8")
    (build / "skip.html").write_text("", encoding="utf-8")
    exclude = tmp_path / "exclude.yml"
    exclude.write_text("- skip.html\n", encoding="utf-8")

    sitemap.main(["-x", str(exclude), str(build), "http://example.com"])

    text = (build / "sitemap.xml").read_text(encoding="utf-8")
    assert "keep.html" in text
    assert "skip.html" not in text


def test_excludes_wildcard(tmp_path):
    build = tmp_path / "build"
    build.mkdir()
    (build / "keep.html").write_text("", encoding="utf-8")
    (build / "skip-one.html").write_text("", encoding="utf-8")
    exclude = tmp_path / "exclude.yml"
    exclude.write_text("- skip-*.html\n", encoding="utf-8")
    sitemap.main(["-x", str(exclude), str(build), "http://example.com"])
    text = (build / "sitemap.xml").read_text(encoding="utf-8")
    assert "keep.html" in text
    assert "skip-one.html" not in text


def test_excludes_regex(tmp_path):
    build = tmp_path / "build"
    build.mkdir()
    (build / "keep.html").write_text("", encoding="utf-8")
    (build / "skip-2.html").write_text("", encoding="utf-8")
    exclude = tmp_path / "exclude.yml"
    exclude.write_text("- regex:skip-\\d\\.html\n", encoding="utf-8")
    sitemap.main(["-x", str(exclude), str(build), "http://example.com"])
    text = (build / "sitemap.xml").read_text(encoding="utf-8")
    assert "keep.html" in text
    assert "skip-2.html" not in text

