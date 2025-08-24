#!/usr/bin/env python3
"""Ensure ``sitemap.xml`` does not reference ``localhost``."""

from __future__ import annotations

import argparse
from pathlib import Path
from pie.cli import create_parser
from pie.logging import configure_logging, logger, log_issue

DEFAULT_LOG = "log/check-sitemap-hostname.txt"


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    """Return parsed command line arguments."""
    parser = create_parser(
        "Verify sitemap.xml does not contain the hostname localhost.",
        log_default=DEFAULT_LOG,
        warnings=True,
    )
    parser.add_argument(
        "file",
        nargs="?",
        default="build/sitemap.xml",
        help="Path to sitemap.xml to verify",
    )
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    """Return ``0`` if ``localhost`` is absent, ``1`` otherwise."""
    args = parse_args(argv)
    Path(args.log).parent.mkdir(parents=True, exist_ok=True)
    configure_logging(args.verbose, args.log)

    path = Path(args.file)
    if not path.is_file():
        if not log_issue("Missing sitemap", path=str(path), warn=args.warn):
            return 1
        return 0
    text = path.read_text(encoding="utf-8")
    if "localhost" in text:
        if not log_issue("Found localhost", path=str(path), warn=args.warn):
            return 1
        return 0
    logger.info("No localhost hostnames found.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
