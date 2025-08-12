#!/usr/bin/env python3
"""Verify that metadata files define an author."""

from __future__ import annotations

import argparse
from pathlib import Path
from typing import Iterable

from pie.logging import logger, add_log_argument, setup_file_logger
from pie.metadata import load_metadata_pair

DEFAULT_LOG = "log/check-author.txt"


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        description="Check that metadata files include an author field.",
    )
    parser.add_argument(
        "directory",
        nargs="?",
        default="src",
        help="Root directory to scan for metadata files",
    )
    add_log_argument(parser, default=DEFAULT_LOG)
    return parser.parse_args(argv)


def _iter_metadata(root: Path) -> Iterable[tuple[list[Path], dict | None]]:
    """Yield ``(paths, metadata)`` pairs for files under *root*.

    Each metadata pair is loaded with :func:`load_metadata_pair` to ensure that
    companion Markdown/YAML files are merged.
    """

    exts = {".md", ".yml", ".yaml"}
    processed: set[Path] = set()

    for path in root.rglob("*"):
        if not path.is_file() or path.suffix.lower() not in exts:
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
    """Entry point for the ``check-author`` console script."""
    args = parse_args(argv)
    Path(args.log).parent.mkdir(parents=True, exist_ok=True)
    setup_file_logger(args.log)

    root = Path(args.directory)
    ok = True
    for paths, meta in _iter_metadata(root):
        author = meta.get("author") if meta else None
        for path in paths:
            if author:
                logger.debug("Found author", path=str(path), author=author)
            else:
                logger.error("Missing author", path=str(path))
                ok = False
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
