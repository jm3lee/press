from __future__ import annotations

import argparse
from pathlib import Path
from typing import Iterable, Sequence

from pie.logging import add_log_argument, setup_file_logger
from pie.update_common import get_changed_files, update_files as update_common_files
from pie.utils import get_pubdate


__all__ = ["main"]


def parse_args(argv: Sequence[str] | None = None) -> argparse.Namespace:
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        description="Update the pubdate field in modified metadata files",
    )
    add_log_argument(parser, default="log/update-pubdate.txt")
    return parser.parse_args(list(argv) if argv is not None else None)


def update_files(paths: Iterable[Path], pubdate: str) -> tuple[list[str], int]:
    """Update ``pubdate`` in files related to *paths*.

    Returns a tuple ``(messages, checked)`` where ``messages`` contains log
    entries for each modified file and ``checked`` is the number of files that
    were examined.
    """
    return update_common_files(paths, "pubdate", pubdate)


def main(argv: Sequence[str] | None = None) -> int:
    """Entry point for the ``update-pubdate`` console script."""
    args = parse_args(argv)
    if args.log:
        Path(args.log).parent.mkdir(parents=True, exist_ok=True)
    setup_file_logger(args.log, level="INFO")
    today = get_pubdate()
    changed = get_changed_files()
    messages, checked = update_files(changed, today)
    for msg in messages:
        print(msg)
    print(f"{checked} {'file' if checked == 1 else 'files'} checked")
    changed_count = len(messages)
    print(f"{changed_count} {'file' if changed_count == 1 else 'files'} changed")
    return 0


if __name__ == "__main__":  # pragma: no cover - manual execution
    raise SystemExit(main())
