#!/usr/bin/env python3
"""Verify that metadata files define breadcrumbs."""

from __future__ import annotations

import argparse
from pathlib import Path
from typing import Iterable
from itertools import chain

from pie.cli import create_parser
from pie.logging import logger, configure_logging
from pie.metadata import load_metadata_pair
from pie.utils import load_exclude_file

DEFAULT_LOG = "log/check-breadcrumbs.txt"
DEFAULT_EXCLUDE = Path("cfg/check-breadcrumbs-exclude.yml")


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    """Parse command line arguments."""
    parser = create_parser(
        "Check that metadata files include a breadcrumbs array.",
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


def _iter_metadata(root: Path) -> Iterable[tuple[list[Path], dict | None]]:
    """Yield ``(paths, metadata)`` pairs for files under *root*.

    Each metadata pair is loaded with :func:`load_metadata_pair` to ensure that
    companion Markdown/YAML files are merged.
    """

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
    """Entry point for the ``check-breadcrumbs`` console script."""
    args = parse_args(argv)
    Path(args.log).parent.mkdir(parents=True, exist_ok=True)
    configure_logging(args.verbose, args.log)

    root = Path(args.directory)
    if args.exclude:
        exclude = load_exclude_file(args.exclude, root)
    elif DEFAULT_EXCLUDE.is_file():
        exclude = load_exclude_file(DEFAULT_EXCLUDE, root)
    else:
        exclude = set()

    ok = True
    for paths, meta in _iter_metadata(root):
        breadcrumbs = meta.get("breadcrumbs") if meta else None
        for path in paths:
            if path.resolve() in exclude:
                continue
            if breadcrumbs:
                logger.debug("Found breadcrumbs", path=str(path))
            else:
                logger.error("Missing breadcrumbs", path=str(path))
                ok = False
    if ok:
        logger.info("All metadata files define breadcrumbs.")
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
