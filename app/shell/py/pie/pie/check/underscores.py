#!/usr/bin/env python3
"""Report URLs containing underscores.

The ``check-underscores`` console script scans HTML files for URLs that
contain underscores and exits with a non-zero status when any are found.
"""

from __future__ import annotations

import argparse
from pathlib import Path
from typing import Iterable

from bs4 import BeautifulSoup

from pie.cli import create_parser
from pie.logging import logger, configure_logging

DEFAULT_LOG = "log/check-underscores.txt"


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    """Parse command line arguments."""
    parser = create_parser(
        "Check HTML files for URLs containing underscores.",
        log_default=DEFAULT_LOG,
    )
    parser.add_argument(
        "directory",
        nargs="?",
        default="build",
        help="Root directory to scan for HTML files",
    )
    return parser.parse_args(argv)


def _iter_urls(path: Path) -> Iterable[str]:
    """Yield URLs discovered in ``href`` and ``src`` attributes."""
    with path.open(encoding="utf-8", errors="ignore") as f:
        soup = BeautifulSoup(f, "html.parser")
    for attr in ("href", "src"):
        for tag in soup.find_all(attrs={attr: True}):
            yield tag[attr]


def main(argv: list[str] | None = None) -> int:
    """Entry point for the ``check-underscores`` console script."""
    args = parse_args(argv)
    Path(args.log).parent.mkdir(parents=True, exist_ok=True)
    configure_logging(args.verbose, args.log)

    root = Path(args.directory)
    bad_urls: set[str] = set()
    for html in root.rglob("*.html"):
        for url in _iter_urls(html):
            if "_" in url:
                logger.error("Underscore in URL", path=str(html), url=url)
                bad_urls.add(url)
    if bad_urls:
        logger.warning("Using dashes instead of underscores in URLs is recommended.")
        for url in sorted(bad_urls):
            logger.warning("Fix URL", url=url)
        return 1
    logger.info("No URLs with underscores found.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
