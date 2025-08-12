from __future__ import annotations

import argparse
import glob
from pathlib import Path
from typing import Iterable, Sequence

import yaml

from pie.logging import add_log_argument, configure_logging, logger
from .common import get_changed_files, update_files as common_update_files

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
    parser = argparse.ArgumentParser(
        description="Update the author field in modified metadata files",
    )
    parser.add_argument(
        "-a",
        "--author",
        default=default_author,
        help="Author name to set; overrides value from cfg/update-author.yml",
    )
    parser.add_argument(
        "paths",
        nargs="*",
        help=(
            "Directories, files, or glob patterns to scan; if omitted, changed files"
            " are read from git"
        ),
    )
    add_log_argument(parser, default="log/update-author.txt")
    parser.add_argument(
        "-v",
        "--verbose",
        action="store_true",
        help="Enable debug logging",
    )
    return parser.parse_args(list(argv) if argv is not None else None)


def update_files(paths: Iterable[Path], author: str) -> tuple[list[str], int]:
    """Update ``author`` in files related to *paths*.

    Returns a tuple ``(messages, checked)`` where ``messages`` contains log
    entries for each modified file and ``checked`` is the number of files that
    were examined.
    """
    return common_update_files(paths, "author", author)


def main(argv: Sequence[str] | None = None) -> int:
    """Entry point for the ``update-author`` console script."""
    args = parse_args(argv)
    if args.log:
        Path(args.log).parent.mkdir(parents=True, exist_ok=True)
    configure_logging(args.verbose, args.log)
    logger.debug("Parsed arguments", args=vars(args))
    if args.paths:
        cwd = Path.cwd()
        changed: list[Path] = []
        for pattern in args.paths:
            matches = glob.glob(pattern, recursive=True) or [pattern]
            for match in matches:
                p = Path(match)
                if not p.exists():
                    continue
                if p.is_dir():
                    for child in p.rglob("*"):
                        if child.suffix in {".md", ".yml", ".yaml"}:
                            changed.append(
                                child.relative_to(cwd) if child.is_absolute() else child
                            )
                else:
                    if p.suffix in {".md", ".yml", ".yaml"}:
                        changed.append(
                            p.relative_to(cwd) if p.is_absolute() else p
                        )
        # Remove duplicates while preserving order
        seen: set[Path] = set()
        unique_changed: list[Path] = []
        for p in changed:
            if p not in seen:
                unique_changed.append(p)
                seen.add(p)
        changed = unique_changed
    else:
        changed = get_changed_files()
    logger.debug("Files to check", files=[str(p) for p in changed])
    messages, checked = update_files(changed, args.author)
    logger.debug("Update complete", messages=messages, checked=checked)
    for msg in messages:
        print(msg)
    print(f"{checked} {'file' if checked == 1 else 'files'} checked")
    changed_count = len(messages)
    print(f"{changed_count} {'file' if changed_count == 1 else 'files'} changed")
    return 0


if __name__ == "__main__":  # pragma: no cover - manual execution
    raise SystemExit(main())

