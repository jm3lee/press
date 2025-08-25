from pie.check import report


def test_parse_errors_groups_by_check() -> None:
    sample = (
        "==> First\n"
        "10:00 a:b:1 E one\n"
        "10:02 e:f:3 W warning\n"
        "==> Second\n"
        "10:01 c:d:2 E two\n"
    )
    result = report.parse_errors(sample)
    assert result == {
        "First": ["10:00 a:b:1 E one", "10:02 e:f:3 W warning"],
        "Second": ["10:01 c:d:2 E two"],
    }


def test_render_html_includes_sections() -> None:
    html = report.render_html({"Check": ["oops"]})
    assert "<h2>Check</h2>" in html
    assert "oops" in html
