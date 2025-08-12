import pytest

from pie.check import unexpanded_jinja


def test_contains_unexpanded_jinja_identifies_and_ignores():
    """"{{a}}" -> True; "no jinja" -> False."""
    assert unexpanded_jinja.contains_unexpanded_jinja("{{a}}")
    assert unexpanded_jinja.contains_unexpanded_jinja("{% if %}")
    assert not unexpanded_jinja.contains_unexpanded_jinja("no jinja")


def test_main_detects_jinja_in_html(tmp_path):
    """HTML with Jinja -> exit 1."""
    build = tmp_path / "build"
    build.mkdir()
    html = build / "page.html"
    html.write_text("<p>{{ a }}</p>", encoding="utf-8")
    rc = unexpanded_jinja.main([str(build)])
    assert rc == 1


def test_main_ignores_jinja_in_pre_and_code(tmp_path):
    """Jinja within ``pre``/``code`` -> exit 0."""
    build = tmp_path / "build"
    build.mkdir()
    html = build / "page.html"
    html.write_text("<pre>{{ a }}</pre><code>{{ b }}</code>", encoding="utf-8")
    rc = unexpanded_jinja.main([str(build)])
    assert rc == 0


def test_main_writes_log_file(tmp_path):
    """Clean HTML -> exit 0 and create log."""
    build = tmp_path / "build"
    build.mkdir()
    html = build / "page.html"
    html.write_text("<p>clean</p>", encoding="utf-8")
    log = tmp_path / "det.log"
    rc = unexpanded_jinja.main([str(build), "--log", str(log)])
    assert rc == 0
    assert log.exists()


def test_parse_args_parses_options():
    """parse_args returns directory and log paths."""
    args = unexpanded_jinja.parse_args(["out", "--log", "log.txt"])
    assert args.directory == "out"
    assert args.log == "log.txt"
