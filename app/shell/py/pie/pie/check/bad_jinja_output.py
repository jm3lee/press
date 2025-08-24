#!/usr/bin/env python3
"""Fail if HTML text nodes contain Python dictionary literals."""

from __future__ import annotations

import argparse
import re
from bs4 import BeautifulSoup
from pie.cli import create_parser
from pie.logging import logger, configure_logging, log_issue

def contains_python_dict(text: str) -> bool:
    """Return ``True`` if *text* looks like a Python dictionary literal."""
    pattern = r"\{[^{}]*:[^{}]*\}"
    return re.search(pattern, text) is not None

def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    """Return parsed command line arguments."""

    parser = create_parser(
        "Check for Python dictionaries in HTML text nodes",
        warnings=True,
    )
    parser.add_argument("html_file", help="Path to the HTML file to inspect")
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    """Return ``0`` if *html_file* is clean, ``1`` otherwise."""

    args = parse_args(argv)

    configure_logging(args.verbose, args.log)

    with open(args.html_file, "r", encoding="utf-8") as f:
        soup = BeautifulSoup(f, "html.parser")

    for line in soup.stripped_strings:
        if contains_python_dict(line):
            if not log_issue(
                "Found Python dictionary in HTML text", line=line, warn=args.warn
            ):
                return 1
            return 0

    logger.debug("No Python dictionaries found in HTML.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
