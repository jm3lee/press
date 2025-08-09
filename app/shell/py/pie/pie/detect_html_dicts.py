#!/usr/bin/env python3
"""Fail if HTML text nodes contain Python dictionary literals."""

from __future__ import annotations

import argparse
import re
from bs4 import BeautifulSoup
from pie.logging import logger, add_log_argument, setup_file_logger

def contains_python_dict(text: str) -> bool:
    """Return ``True`` if *text* looks like a Python dictionary literal."""
    pattern = r"\{[^{}]*:[^{}]*\}"
    return re.search(pattern, text) is not None

def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    """Return parsed command line arguments."""

    parser = argparse.ArgumentParser(
        description="Check for Python dictionaries in HTML text nodes",
    )
    parser.add_argument("html_file", help="Path to the HTML file to inspect")
    add_log_argument(parser)
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    """Return ``0`` if *html_file* is clean, ``1`` otherwise."""

    args = parse_args(argv)

    setup_file_logger(args.log)

    with open(args.html_file, "r", encoding="utf-8") as f:
        soup = BeautifulSoup(f, "html.parser")

    for line in soup.stripped_strings:
        if contains_python_dict(line):
            logger.error("Found Python dictionary in HTML text", line=line)
            return 1

    logger.debug("No Python dictionaries found in HTML.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
