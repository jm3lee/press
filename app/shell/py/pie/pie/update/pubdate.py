from __future__ import annotations

import argparse
from pathlib import Path
from typing import Iterable, Sequence

from pie.cli import create_parser
from pie.logging import configure_logging, logger
from .common import get_changed_files, update_files as common_update_files
from pie.utils import get_pubdate


__all__ = ["main"]


def parse_args(argv: Sequence[str] | None = None) -> argparse.Namespace:
    """Parse command line arguments."""
    parser = create_parser(
        "Update the pubdate field in modified metadata files",
        log_default="log/update-pubdate.txt",
    )
    parser.add_argument(
        "--sort-keys",
        action="store_true",
        help="Sort keys when writing YAML output",
    )
    return parser.parse_args(list(argv) if argv is not None else None)


def update_files(
    paths: Iterable[Path], pubdate: str, sort_keys: bool = False
) -> tuple[list[str], int]:
    """Update ``pubdate`` in files related to *paths*.

    Returns a tuple ``(messages, checked)`` where ``messages`` contains log
    entries for each modified file and ``checked`` is the number of files that
    were examined. When ``sort_keys`` is true YAML mappings are serialized with
    keys in sorted order.
    """
    return common_update_files(paths, "doc.pubdate", pubdate, sort_keys=sort_keys)


def main(argv: Sequence[str] | None = None) -> int:
    """Entry point for the ``update-pubdate`` console script."""
    args = parse_args(argv)
    if args.log:
        Path(args.log).parent.mkdir(parents=True, exist_ok=True)
    configure_logging(args.verbose, args.log)
    today = get_pubdate()
    changed = get_changed_files()
    changed = list(filter(lambda p: str(p).startswith("src/"), changed))
    messages, checked = update_files(changed, today, args.sort_keys)
    changed_count = len(messages)
    logger.info(f"Summary", checked=checked, changed_count=changed_count)
    return 0


if __name__ == "__main__":  # pragma: no cover - manual execution
    raise SystemExit(main())
