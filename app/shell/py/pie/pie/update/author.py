from __future__ import annotations

import argparse
from pathlib import Path
from typing import Iterable, Sequence

import yaml

from pie.logging import add_log_argument, setup_file_logger
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
        "path",
        nargs="?",
        type=Path,
        help="Directory or file to scan; if omitted, changed files are read from git",
    )
    add_log_argument(parser, default="log/update-author.txt")
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
    setup_file_logger(args.log, level="INFO")
    if args.path:
        cwd = Path.cwd()
        if args.path.is_dir():
            changed = [
                (p.relative_to(cwd) if p.is_absolute() else p)
                for p in args.path.rglob("*")
                if p.suffix in {".md", ".yml", ".yaml"}
            ]
        else:
            changed = [
                args.path.relative_to(cwd) if args.path.is_absolute() else args.path
            ] if args.path.suffix in {".md", ".yml", ".yaml"} else []
    else:
        changed = get_changed_files()
    messages, checked = update_files(changed, args.author)
    for msg in messages:
        print(msg)
    print(f"{checked} {'file' if checked == 1 else 'files'} checked")
    changed_count = len(messages)
    print(f"{changed_count} {'file' if changed_count == 1 else 'files'} changed")
    return 0


if __name__ == "__main__":  # pragma: no cover - manual execution
    raise SystemExit(main())

