"""Remove deprecated ``name`` fields from metadata files.

This script scans a directory for Markdown and YAML files and removes the
top‑level ``name`` field from each file's metadata. It is intended as a
one‑time cleanup tool while deprecating the ``name`` field in favour of
``title``/``citation``.
"""

from __future__ import annotations

import argparse
from pathlib import Path
from typing import Iterable, Sequence, Tuple

from pie.logging import add_log_argument, configure_logging

__all__ = ["main", "remove_name_fields"]


def remove_name_from_yaml(path: Path) -> tuple[bool, str | None]:
    """Remove ``name`` from a YAML file.

    Returns ``(changed, value)`` where ``value`` is the removed field's value
    if a change occurred.
    """

    lines = path.read_text(encoding="utf-8").splitlines(keepends=True)
    new_lines = []
    removed: str | None = None
    for line in lines:
        if line.startswith("name:"):
            removed = line.split(":", 1)[1].strip()
            continue
        new_lines.append(line)
    if removed is not None:
        path.write_text("".join(new_lines), encoding="utf-8")
        return True, removed
    return False, None


def remove_name_from_markdown(path: Path) -> tuple[bool, str | None]:
    """Remove ``name`` from Markdown front matter."""

    lines = path.read_text(encoding="utf-8").splitlines(keepends=True)
    if not lines or not lines[0].startswith("---"):
        return False, None
    try:
        end = next(i for i, line in enumerate(lines[1:], start=1) if line.startswith("---"))
    except StopIteration:
        return False, None
    new_lines = lines[:1]
    removed: str | None = None
    for line in lines[1:end]:
        if line.startswith("name:"):
            removed = line.split(":", 1)[1].strip()
            continue
        new_lines.append(line)
    new_lines.extend(lines[end:])
    if removed is not None:
        path.write_text("".join(new_lines), encoding="utf-8")
        return True, removed
    return False, None


def remove_name_fields(paths: Iterable[Path]) -> tuple[list[str], int]:
    """Remove ``name`` from all *paths*.

    Returns a tuple ``(messages, checked)`` with log messages for each
    modified file and the number of files examined.
    """

    changes: list[str] = []
    checked = 0
    for path in paths:
        if path.suffix in {".yml", ".yaml"}:
            checked += 1
            changed, val = remove_name_from_yaml(path)
        elif path.suffix == ".md":
            checked += 1
            changed, val = remove_name_from_markdown(path)
        else:
            continue
        if changed and val is not None:
            changes.append(f"{path}: {val}")
    return changes, checked


def walk_files(root: Path) -> Iterable[Path]:
    """Yield metadata files under *root*."""

    for path in root.rglob("*"):
        if path.suffix.lower() in {".md", ".yml", ".yaml"} and path.is_file():
            yield path


def parse_args(argv: Sequence[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Remove deprecated 'name' fields from metadata files",
    )
    parser.add_argument(
        "root",
        help="Root directory to scan",
    )
    add_log_argument(parser)
    parser.add_argument(
        "-v",
        "--verbose",
        action="store_true",
        help="Enable debug logging",
    )
    return parser.parse_args(list(argv) if argv is not None else None)


def main(argv: Sequence[str] | None = None) -> int:
    args = parse_args(argv)
    configure_logging(args.verbose, args.log)
    root = Path(args.root)
    changes, checked = remove_name_fields(walk_files(root))
    for msg in changes:
        print(msg)
    print(f"{checked} {'file' if checked == 1 else 'files'} checked")
    print(f"{len(changes)} {'file' if len(changes) == 1 else 'files'} changed")
    return 0


if __name__ == "__main__":  # pragma: no cover - manual execution
    raise SystemExit(main())

