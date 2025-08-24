from pie.check import sitemap_hostname as check_sitemap_hostname


def test_main_reports_localhost(tmp_path):
    """If sitemap references localhost -> exit code 1."""
    sm = tmp_path / "sitemap.xml"
    sm.write_text("<loc>http://localhost/foo</loc>", encoding="utf-8")
    rc = check_sitemap_hostname.main([str(sm), "-l", str(tmp_path / "log.txt")])
    assert rc == 1


def test_main_passes_and_logs(tmp_path):
    """No localhost -> exit 0 and create log."""
    sm = tmp_path / "sitemap.xml"
    sm.write_text("<loc>https://example.com/foo</loc>", encoding="utf-8")
    log = tmp_path / "log.txt"
    rc = check_sitemap_hostname.main([str(sm), "-l", str(log)])
    assert rc == 0
    assert log.exists()


def test_parse_args_defaults():
    """parse_args returns default paths."""
    args = check_sitemap_hostname.parse_args([])
    assert args.file == "build/sitemap.xml"
    assert args.log == "log/check-sitemap-hostname.txt"
