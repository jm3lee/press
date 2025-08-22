"""Check that HTML files contain non-empty ``<h1>`` tags.

This module provides a ``check-page-title`` console script that scans a
directory tree for HTML files and verifies that each file contains a first
level heading.  It mirrors the behaviour of the legacy
``app/shell/bin/check-page-title`` script.
"""

from __future__ import annotations

import argparse
import os
import sys
from pathlib import Path

from bs4 import BeautifulSoup
from pie.cli import create_parser
from pie.logging import configure_logging
from pie.utils import load_exclude_file


# Detect whether we should emit ANSI colour codes. We only use colours when
# stdout is a TTY and the TERM environment variable is not set to "dumb".
USE_COLOR = sys.stdout.isatty() and os.environ.get("TERM") != "dumb"

GREEN = "\x1b[32m" if USE_COLOR else ""
REVERSE = "\x1b[7m" if USE_COLOR else ""
RESET = "\x1b[0m" if USE_COLOR else ""


def check_file(path: Path) -> bool:
    """Return ``True`` if ``path`` contains a non-empty ``<h1>`` tag."""
    with open(path, "r", encoding="utf-8") as f:
        soup = BeautifulSoup(f, "html.parser")
    h1 = soup.find("h1")
    if h1 is None or not h1.get_text(strip=True):
        message = f"Missing or empty <h1> in {path}"
        if USE_COLOR:
            print(f"{REVERSE}{message}{RESET}")
        else:
            print(message)
        return False
    return True


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    """Parse command line arguments."""
    parser = create_parser(
        "Verify that HTML files contain non-empty <h1> tags."
    )
    parser.add_argument(
        "directory",
        nargs="?",
        default="build",
        help="Root directory to scan for HTML files",
    )
    parser.add_argument(
        "-x",
        "--exclude",
        help="YAML file listing HTML files to skip",
    )
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    """Entry point used by the ``check-page-title`` console script."""
    args = parse_args(argv)
    configure_logging(args.verbose, args.log)
    directory = Path(args.directory).resolve()
    html_files = list(directory.rglob("*.html"))
    exclude = load_exclude_file(args.exclude, directory)
    ok = True
    for html_file in html_files:
        if html_file.resolve() in exclude:
            continue
        if not check_file(html_file):
            ok = False
    if ok:
        message = "All pages have <h1> titles."
        if USE_COLOR:
            print(f"{GREEN}{message}{RESET}")
        else:
            print(message)
        return 0
    return 1


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))

