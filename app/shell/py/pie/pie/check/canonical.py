#!/usr/bin/env python3
"""Ensure canonical links do not reference ``localhost``."""

from __future__ import annotations

import argparse
from pathlib import Path
from urllib.parse import urlparse

from bs4 import BeautifulSoup

from pie.cli import create_parser
from pie.logging import configure_logging, logger

DEFAULT_LOG = "log/check-canonical.txt"


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    """Return parsed command line arguments."""
    parser = create_parser(
        "Verify canonical links do not reference the hostname localhost.",
        log_default=DEFAULT_LOG,
    )
    parser.add_argument(
        "directory",
        nargs="?",
        default="build",
        help="Root directory containing HTML files to verify",
    )
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    """Return ``0`` if no canonical links reference localhost, ``1`` otherwise."""
    args = parse_args(argv)
    Path(args.log).parent.mkdir(parents=True, exist_ok=True)
    configure_logging(args.verbose, args.log)

    root = Path(args.directory)
    found = False
    for html in root.rglob("*.html"):
        with html.open(encoding="utf-8", errors="ignore") as f:
            soup = BeautifulSoup(f, "html.parser")
        for tag in soup.find_all("link", rel="canonical", href=True):
            href = tag["href"]
            if urlparse(href).hostname == "localhost":
                logger.error(
                    "Canonical link references localhost", path=str(html), href=href
                )
                found = True
    if not found:
        logger.info("No canonical links pointing to localhost found.")
    return 1 if found else 0


if __name__ == "__main__":
    raise SystemExit(main())
