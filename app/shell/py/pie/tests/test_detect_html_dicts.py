import pytest

from pie import detect_html_dicts


def test_contains_python_dict_identifies_and_ignores():
    """"{'a': 1}" -> True; "no dict here" -> False."""
    assert detect_html_dicts.contains_python_dict("{'a': 1}")
    assert not detect_html_dicts.contains_python_dict("no dict here")
    assert not detect_html_dicts.contains_python_dict("{0}")


def test_main_detects_dict_in_html(tmp_path):
    """HTML with dict -> exit 1."""
    html = tmp_path / "page.html"
    html.write_text("<p>{'a': 1}</p>", encoding="utf-8")
    rc = detect_html_dicts.main([str(html)])
    assert rc == 1


def test_main_writes_log_file(tmp_path):
    """Clean HTML -> exit 0 and create log."""
    html = tmp_path / "clean.html"
    html.write_text("<p>No dict</p>", encoding="utf-8")
    log = tmp_path / "det.log"
    rc = detect_html_dicts.main([str(html), "--log", str(log)])
    assert rc == 0
    assert log.exists()


def test_parse_args_parses_options():
    """parse_args returns file and log paths."""
    args = detect_html_dicts.parse_args(["file.html", "--log", "log.txt"])
    assert args.html_file == "file.html"
    assert args.log == "log.txt"
