#!/usr/bin/env python3
"""Fail if HTML files contain unexpanded Jinja outside ``pre``/``code`` blocks."""

from __future__ import annotations

import argparse
from pathlib import Path
from bs4 import BeautifulSoup
from pie.cli import create_parser
from pie.logging import configure_logging, log_issue

DEFAULT_LOG = "log/check-unexpanded-jinja.txt"


def contains_unexpanded_jinja(text: str) -> bool:
    """Return ``True`` when *text* includes Jinja markers."""
    return "{{" in text or "{%" in text


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    """Return parsed command line arguments."""

    parser = create_parser(
        "Check for unexpanded Jinja code in HTML files.",
        log_default=DEFAULT_LOG,
        warnings=True,
    )
    parser.add_argument(
        "directory",
        nargs="?",
        default="build",
        help="Root directory containing HTML files",
    )
    return parser.parse_args(argv)


def check_file(path: Path, warn: bool) -> bool:
    """Return ``True`` if *path* is free of unexpanded Jinja."""
    with open(path, "r", encoding="utf-8") as f:
        soup = BeautifulSoup(f, "html.parser")

    for text in soup.find_all(string=True):
        if text.find_parent(["pre", "code"]):
            continue
        if contains_unexpanded_jinja(text):
            if not log_issue(
                "Found unexpanded Jinja", path=str(path), snippet=text.strip(), warn=warn
            ):
                return False

    for tag in soup.find_all(True):
        if tag.name in {"pre", "code"} or tag.find_parent(["pre", "code"]):
            continue
        for value in tag.attrs.values():
            values = value if isinstance(value, (list, tuple)) else [value]
            for v in values:
                if isinstance(v, str) and contains_unexpanded_jinja(v):
                    if not log_issue(
                        "Found unexpanded Jinja", path=str(path), snippet=v.strip(), warn=warn
                    ):
                        return False
    return True


def main(argv: list[str] | None = None) -> int:
    """Return ``0`` if HTML files are clean, ``1`` otherwise."""

    args = parse_args(argv)
    Path(args.log).parent.mkdir(parents=True, exist_ok=True)
    configure_logging(args.verbose, args.log)

    base = Path(args.directory)
    html_files = list(base.rglob("*.html"))

    ok = True
    for html_file in html_files:
        if not check_file(html_file, args.warn):
            ok = False

    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
