#!/usr/bin/env python3
"""Report unescaped dollar signs in Markdown files."""

from __future__ import annotations

import argparse
from pathlib import Path
from pie.cli import create_parser
from pie.logging import configure_logging, logger
from pie.utils import load_exclude_file

DEFAULT_LOG = "log/check-unescaped-dollar.txt"
DEFAULT_EXCLUDE = Path("cfg/check-unescaped-dollar-exclude.yml")


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    """Return parsed command line arguments."""
    parser = create_parser(
        "Check Markdown files for unescaped dollar signs.",
        log_default=DEFAULT_LOG,
    )
    parser.add_argument(
        "directory",
        nargs="?",
        default="src",
        help="Root directory to scan for Markdown files",
    )
    parser.add_argument(
        "-x",
        "--exclude",
        help=(
            "YAML file listing Markdown files to skip "
            f"(default: {DEFAULT_EXCLUDE})"
        ),
    )
    return parser.parse_args(argv)


def _has_single_dollar(text: str) -> bool:
    text = text.replace("\\$", "")
    for line in text.splitlines():
        if line.count("$") % 2:
            return True
    return False


def main(argv: list[str] | None = None) -> int:
    """Entry point for the ``check-unescaped-dollar`` console script."""
    args = parse_args(argv)
    Path(args.log).parent.mkdir(parents=True, exist_ok=True)
    configure_logging(args.verbose, args.log)

    root = Path(args.directory)
    if args.exclude:
        exclude_file = args.exclude
    elif DEFAULT_EXCLUDE.is_file():
        exclude_file = DEFAULT_EXCLUDE
    else:
        exclude_file = None
    exclude = load_exclude_file(exclude_file, root)
    ok = True
    for md in root.rglob("*.md"):
        if md in exclude:
            continue
        text = md.read_text(encoding="utf-8")
        if _has_single_dollar(text):
            logger.error("Unescaped dollar sign", path=str(md))
            ok = False
    if ok:
        logger.info("No unescaped dollar signs found.")
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
