#!/usr/bin/env python3
"""Verify that metadata files define ``doc.author``."""

from __future__ import annotations

import argparse
from pathlib import Path
from typing import Iterator
from itertools import chain

from pie.cli import create_parser
from pie.logging import logger, configure_logging
from pie.metadata import load_metadata_pair
from pie.utils import load_exclude_file

DEFAULT_LOG = "log/check-author.txt"
DEFAULT_EXCLUDE = Path("cfg/check-author-exclude.yml")


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    """Parse command line arguments."""
    parser = create_parser(
        "Check that metadata files include a doc.author field.",
        log_default=DEFAULT_LOG,
    )
    parser.add_argument(
        "directory",
        nargs="?",
        default="src",
        help="Root directory to scan for metadata files",
    )
    parser.add_argument(
        "-x",
        "--exclude",
        help=(
            "YAML file listing metadata files to skip "
            f"(default: {DEFAULT_EXCLUDE})"
        ),
    )
    return parser.parse_args(argv)


def _iter_metadata(
    root: Path,
    base_dir: Path,
) -> Iterator[tuple[Path, list[Path], dict | None]]:
    """Yield ``(metadata_path, paths, metadata)`` for files under *root*.

    Each metadata pair is loaded with :func:`load_metadata_pair` to ensure that
    companion Markdown/YAML files are merged.
    """

    processed: set[Path] = set()

    for path in chain(
        root.rglob("*.md"),
        root.rglob("*.yml"),
        root.rglob("*.yaml"),
    ):
        if not path.is_file():
            continue
        base = path.with_suffix("")
        if base in processed:
            continue
        processed.add(base)
        try:
            source = path.relative_to(base_dir)
        except ValueError:
            source = path
        meta = load_metadata_pair(source)
        if meta and "path" in meta:
            paths = []
            for raw in meta["path"]:
                candidate = Path(raw)
                if candidate.is_absolute():
                    resolved_candidate = candidate.resolve()
                else:
                    resolved_candidate = (base_dir / candidate).resolve()
                paths.append(resolved_candidate)
        else:
            paths = [path]
        yield path, paths, meta


def main(argv: list[str] | None = None) -> int:
    """Entry point for the ``check-author`` console script."""
    args = parse_args(argv)
    Path(args.log).parent.mkdir(parents=True, exist_ok=True)
    configure_logging(args.verbose, args.log)

    root = Path(args.directory)
    scan_root = root if root.is_absolute() else (Path.cwd() / root).resolve()
    if args.exclude:
        exclude_file = Path(args.exclude)
    elif DEFAULT_EXCLUDE.is_file():
        exclude_file = DEFAULT_EXCLUDE
    else:
        exclude_file = None
    exclude = load_exclude_file(exclude_file, scan_root)

    ok = True
    base_dir = scan_root.parent
    for metadata_path, paths, meta in _iter_metadata(scan_root, base_dir):
        if metadata_path in exclude:
            continue
        doc = meta.get("doc") if meta else None
        author = doc.get("author") if isinstance(doc, dict) else None
        for path in paths:
            if path in exclude:
                continue
            try:
                display_path = path.relative_to(scan_root)
            except ValueError:
                display_path = path
            if author:
                logger.debug(
                    "Found doc.author", path=str(display_path), author=author
                )
            else:
                logger.error("Missing doc.author", path=str(display_path))
                ok = False
    if ok:
        logger.info("All metadata files define doc.author.")
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
