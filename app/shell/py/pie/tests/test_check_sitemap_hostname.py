import runpy
import sys
from pathlib import Path

import pytest

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


def test_main_missing_file(tmp_path):
    """Absent sitemap file -> exit code 1."""
    rc = check_sitemap_hostname.main(
        [str(tmp_path / "sitemap.xml"), "-l", str(tmp_path / "log.txt")]
    )
    assert rc == 1


def test_run_module_as_script(tmp_path, monkeypatch):
    """Executing module as a script exits via :class:`SystemExit`."""
    monkeypatch.chdir(tmp_path)
    monkeypatch.syspath_prepend(str(Path(__file__).resolve().parents[1]))
    monkeypatch.setattr(sys, "argv", ["sitemap_hostname.py"])
    with pytest.raises(SystemExit) as excinfo:
        runpy.run_module(
            "pie.check.sitemap_hostname", run_name="__main__", alter_sys=True
        )
    assert excinfo.value.code == 1
