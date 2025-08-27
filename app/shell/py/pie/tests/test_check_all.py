from __future__ import annotations

import runpy
import sys
import types

import pytest

from pie.check import all as check_all


def test_main_ok(monkeypatch, capsys) -> None:
    """Return code 0 when all checks pass."""
    monkeypatch.setattr(
        check_all,
        "CHECKS",
        [("First", lambda: 0), ("Second", lambda: 0)],
    )
    rc = check_all.main()
    out = capsys.readouterr().out
    assert rc == 0
    assert "==> First" in out
    assert "==> Second" in out


def test_main_failure(monkeypatch) -> None:
    """Return code 1 when a check fails."""
    monkeypatch.setattr(
        check_all,
        "CHECKS",
        [("One", lambda: 0), ("Two", lambda: 1)],
    )
    rc = check_all.main()
    assert rc == 1


def test_extra_checks(monkeypatch, tmp_path, capsys) -> None:
    """Load and run extra checkers from a YAML file."""
    called = False

    def run() -> int:
        nonlocal called
        called = True
        return 0

    mod = types.ModuleType("my_check")
    mod.run = run
    monkeypatch.setitem(sys.modules, "my_check", mod)
    cfg = tmp_path / "extra.yml"
    cfg.write_text("- my_check:run\n", encoding="utf-8")
    monkeypatch.setattr(check_all, "EXTRA_CHECKS_PATH", cfg)
    monkeypatch.setattr(check_all, "BUILTIN_CHECKS", ())
    check_all.CHECKS = check_all.BUILTIN_CHECKS + tuple(
        check_all.load_extra_checks()
    )
    rc = check_all.main()
    out = capsys.readouterr().out
    assert rc == 0
    assert called
    assert "Custom: my_check:run" in out


def test_run_as_script(monkeypatch) -> None:
    """The module exits via SystemExit when run as a script."""
    check_pkg = types.ModuleType("pie.check")
    monkeypatch.setitem(sys.modules, "pie.check", check_pkg)
    for name in [
        "author",
        "bad_mathjax",
        "unescaped_dollar",
        "page_title",
        "post_build",
        "unexpanded_jinja",
        "underscores",
        "canonical",
        "sitemap_hostname",
    ]:
        mod = types.ModuleType(f"pie.check.{name}")
        mod.main = lambda _a, _name=name: 0
        setattr(check_pkg, name, mod)
        monkeypatch.setitem(sys.modules, f"pie.check.{name}", mod)

    with pytest.raises(SystemExit) as excinfo:
        runpy.run_module("pie.check.all", run_name="__main__")
    assert excinfo.value.code == 0
