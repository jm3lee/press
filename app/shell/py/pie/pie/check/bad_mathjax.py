#!/usr/bin/env python3
"""Fail if Markdown files use \(\) or \[\] math delimiters."""

from __future__ import annotations

import argparse
import re
from pathlib import Path

from pie.cli import create_parser
from pie.logging import configure_logging, logger

DEFAULT_LOG = "log/check-bad-mathjax.txt"
PATTERNS = [
    re.compile(r"\\\([^\n]*?\\\)"),
    re.compile(r"\\\[[^\n]*?\\\]"),
]


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    """Return parsed command line arguments."""
    parser = create_parser(
        "Check Markdown files for LaTeX delimiters \\(\\) or \\[\\]",
        log_default=DEFAULT_LOG,
    )
    parser.add_argument(
        "directory",
        nargs="?",
        default="src",
        help="Root directory to scan for Markdown files",
    )
    return parser.parse_args(argv)


def _has_bad_math(text: str) -> bool:
    return any(pattern.search(text) for pattern in PATTERNS)


def main(argv: list[str] | None = None) -> int:
    """Entry point for the ``check-bad-mathjax`` console script."""
    args = parse_args(argv)
    Path(args.log).parent.mkdir(parents=True, exist_ok=True)
    configure_logging(args.verbose, args.log)

    root = Path(args.directory)
    ok = True
    for md in root.rglob("*.md"):
        text = md.read_text(encoding="utf-8")
        if _has_bad_math(text):
            logger.error("Found bad math delimiter", path=str(md))
            ok = False
    if ok:
        logger.info("No bad math delimiters found.")
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
