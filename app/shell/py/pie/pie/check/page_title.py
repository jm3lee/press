"""Check that HTML files contain non-empty ``<h1>`` tags.

This module provides a ``check-page-title`` console script that scans a
directory tree for HTML files and verifies that each file contains a first
level heading.  It mirrors the behaviour of the legacy
``app/shell/bin/check-page-title`` script.
"""

from __future__ import annotations

import argparse
from pathlib import Path

from bs4 import BeautifulSoup
from pie.cli import create_parser
from pie.logging import configure_logging, logger
from pie.utils import load_exclude_file


DEFAULT_LOG = "log/check-page-title.txt"
DEFAULT_EXCLUDE = Path("cfg/check-page-title-exclude.yml")


def check_file(path: Path) -> bool:
    """Return ``True`` if ``path`` contains a non-empty ``<h1>`` tag."""
    with path.open("r", encoding="utf-8") as f:
        soup = BeautifulSoup(f, "html.parser")
    h1 = soup.find("h1")
    if h1 is None or not h1.get_text(strip=True):
        logger.error("Missing or empty <h1>", path=str(path))
        return False
    return True


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    """Parse command line arguments."""
    parser = create_parser(
        "Verify that HTML files contain non-empty <h1> tags.",
        log_default=DEFAULT_LOG,
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
        help=(
            "YAML file listing HTML files to skip "
            f"(default: {DEFAULT_EXCLUDE})"
        ),
    )
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    """Entry point used by the ``check-page-title`` console script."""
    args = parse_args(argv)
    Path(args.log).parent.mkdir(parents=True, exist_ok=True)
    configure_logging(args.verbose, args.log)

    directory = Path(args.directory).resolve()
    html_files = list(directory.rglob("*.html"))
    if args.exclude:
        exclude = load_exclude_file(args.exclude, directory)
    elif DEFAULT_EXCLUDE.is_file():
        exclude = load_exclude_file(DEFAULT_EXCLUDE, directory)
    else:
        exclude = set()

    ok = True
    for html_file in html_files:
        if html_file.resolve() in exclude:
            continue
        if not check_file(html_file):
            ok = False
    if ok:
        logger.info("All pages have <h1> titles.")
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())

