from __future__ import annotations

import argparse
from pathlib import Path
from typing import Iterable, Sequence

import yaml

from pie.cli import create_parser
from pie.logging import configure_logging, logger
from .common import (
    collect_paths,
    get_changed_files,
    update_files as common_update_files,
)

__all__ = ["main"]


def load_default_author(cfg_path: Path | None = None) -> str:
    """Return the default author from ``cfg/update-author.yml``."""
    path = cfg_path or Path("cfg") / "update-author.yml"
    try:
        data = yaml.safe_load(path.read_text(encoding="utf-8"))
    except FileNotFoundError:
        return ""
    if isinstance(data, dict):
        return str(data.get("author", ""))
    if isinstance(data, str):
        return data
    return ""


def parse_args(argv: Sequence[str] | None = None) -> argparse.Namespace:
    """Parse command line arguments."""
    default_author = load_default_author()
    parser = create_parser(
        "Update the author field in modified metadata files",
        log_default="log/update-author.txt",
    )
    parser.add_argument(
        "-a",
        "--author",
        default=default_author,
        help="Author name to set; overrides value from cfg/update-author.yml",
    )
    parser.add_argument(
        "--sort-keys",
        action="store_true",
        help="Sort keys when writing YAML output",
    )
    parser.add_argument(
        "paths",
        nargs="*",
        help=(
            "Directories, files, or glob patterns to scan; if omitted, changed files"
            " are read from git"
        ),
    )
    return parser.parse_args(list(argv) if argv is not None else None)


def update_files(
    paths: Iterable[Path], author: str, sort_keys: bool = False
) -> tuple[list[str], int]:
    """Update ``author`` in files related to *paths*.

    Returns a tuple ``(messages, checked)`` where ``messages`` contains log
    entries for each modified file and ``checked`` is the number of files that
    were examined. When ``sort_keys`` is true YAML mappings are serialized with
    keys in sorted order.
    """
    return common_update_files(paths, "author", author, sort_keys=sort_keys)


def main(argv: Sequence[str] | None = None) -> int:
    """Entry point for the ``update-author`` console script."""
    args = parse_args(argv)
    if args.log:
        Path(args.log).parent.mkdir(parents=True, exist_ok=True)
    configure_logging(args.verbose, args.log)
    logger.debug("Parsed arguments", args=vars(args))
    if args.paths:
        changed = collect_paths(args.paths)
    else:
        changed = get_changed_files()
        changed = list(filter(lambda p: str(p).startswith("src/"), changed))
    logger.debug("Files to check", files=[str(p) for p in changed])
    messages, checked = update_files(changed, args.author, args.sort_keys)
    logger.debug("Update complete", messages=messages, checked=checked)
    for msg in messages:
        print(msg)
    print(f"{checked} {'file' if checked == 1 else 'files'} checked")
    changed_count = len(messages)
    print(f"{changed_count} {'file' if changed_count == 1 else 'files'} changed")
    return 0


if __name__ == "__main__":  # pragma: no cover - manual execution
    raise SystemExit(main())

