#!/usr/bin/env python3
"""Ensure that all defined permalinks are unique."""

from __future__ import annotations

import argparse
from itertools import chain
from pathlib import Path
from typing import Iterable

from pie.cli import create_parser
from pie.logging import configure_logging, logger
from pie.metadata import load_metadata_pair

DEFAULT_LOG = "log/check-permalinks.txt"


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    """Parse command line arguments."""
    parser = create_parser(
        "Verify that permalink metadata values are unique.",
        log_default=DEFAULT_LOG,
    )
    parser.add_argument(
        "directory",
        nargs="?",
        default="src",
        help="Root directory to scan for metadata files",
    )
    return parser.parse_args(argv)


def _iter_metadata(root: Path) -> Iterable[tuple[list[Path], dict | None]]:
    """Yield ``(paths, metadata)`` pairs for files under *root*."""
    processed: set[Path] = set()
    for path in chain(root.rglob("*.md"), root.rglob("*.yml"), root.rglob("*.yaml")):
        if not path.is_file():
            continue
        base = path.with_suffix("")
        if base in processed:
            continue
        processed.add(base)
        meta = load_metadata_pair(path)
        if meta and "path" in meta:
            paths = [Path(p) for p in meta["path"]]
        else:
            paths = [path]
        yield paths, meta


def main(argv: list[str] | None = None) -> int:
    """Entry point for the ``check-permalinks`` console script."""
    args = parse_args(argv)
    Path(args.log).parent.mkdir(parents=True, exist_ok=True)
    configure_logging(args.verbose, args.log)

    root = Path(args.directory)
    seen: dict[str, Path] = {}
    ok = True
    for paths, meta in _iter_metadata(root):
        permalink = meta.get("permalink") if meta else None
        if permalink:
            if permalink in seen:
                for path in paths:
                    logger.error(
                        "Duplicate permalink",
                        permalink=permalink,
                        path=str(path),
                        other=str(seen[permalink]),
                    )
                ok = False
            else:
                seen[permalink] = paths[0]
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
