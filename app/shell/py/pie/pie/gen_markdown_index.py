#!/usr/bin/env python3
"""Generate a Markdown index from YAML metadata files.

This module is deprecated and will be removed in a future release.
"""

from __future__ import annotations

import argparse
import warnings
from pathlib import Path
from typing import Iterator

from pie.logging import add_log_argument, configure_logging
from pie.index_tree import walk, getopt_link, getopt_show

warnings.warn(
    "pie.gen_markdown_index is deprecated and will be removed in a future release",
    DeprecationWarning,
    stacklevel=2,
)


def generate(directory: Path, level: int = 0) -> Iterator[str]:
    """Yield Markdown list items for *directory* recursively."""
    entries = sorted(walk(directory), key=lambda x: x[0]["title"].lower())
    for meta, path in entries:
        entry_id = meta["id"]
        title = meta["title"]
        link = getopt_link(meta)
        show = getopt_show(meta)
        if show:
            if link:
                yield "  " * level + f'- {{{{ linktitle("{entry_id}") }}}}'
            else:
                yield "  " * level + f"- {{{{'{title}'|title}}}}"
        if path.is_dir():
            if show:
                yield from generate(path, level + 1)
            else:
                yield from generate(path, level)


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Generate a Markdown index")
    parser.add_argument("root_dir", nargs="?", default=".", help="Root directory to scan")
    add_log_argument(parser)
    parser.add_argument(
        "-v",
        "--verbose",
        action="store_true",
        help="Enable debug logging",
    )
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    """Entry point for the ``gen-markdown-index`` console script."""
    args = parse_args(argv)
    configure_logging(args.verbose, args.log)
    for line in generate(Path(args.root_dir)):
        print(line)
    return 0


if __name__ == "__main__":  # pragma: no cover - manual execution
    raise SystemExit(main())
