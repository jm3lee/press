"""Rename deprecated 'gen-markdown-index' metadata to 'indextree'."""

from __future__ import annotations

import argparse
from pathlib import Path
from typing import Iterable, Sequence
import io

from pie.cli import create_parser
from pie.logging import configure_logging, logger
from pie.utils import yaml

__all__ = ["main"]


def _upgrade_yaml(path: Path) -> bool:
    """Return ``True`` if *path* was updated."""

    data = yaml.load(path.read_text(encoding="utf-8")) or {}
    section = data.pop("gen-markdown-index", None)
    if section is None:
        return False
    data["indextree"] = section
    buf = io.StringIO()
    yaml.dump(data, buf)
    path.write_text(buf.getvalue(), encoding="utf-8")
    return True


def _upgrade_markdown(path: Path) -> bool:
    """Return ``True`` if the front matter in *path* was updated."""

    lines = path.read_text(encoding="utf-8").splitlines(keepends=True)
    if not lines or not lines[0].startswith("---"):
        return False
    try:
        end = next(i for i, line in enumerate(lines[1:], start=1) if line.startswith("---"))
    except StopIteration:
        return False
    front = yaml.load("".join(lines[1:end])) or {}
    section = front.pop("gen-markdown-index", None)
    if section is None:
        return False
    front["indextree"] = section
    buf = io.StringIO()
    yaml.dump(front, buf)
    new_front = buf.getvalue().splitlines(keepends=True)
    path.write_text("".join(["---\n", *new_front, *lines[end:]]), encoding="utf-8")
    return True


def upgrade_file(path: Path) -> bool:
    """Upgrade metadata in *path*."""

    if path.suffix.lower() in {".yml", ".yaml"}:
        return _upgrade_yaml(path)
    if path.suffix.lower() == ".md":
        return _upgrade_markdown(path)
    return False


def walk_files(paths: Iterable[Path]) -> Iterable[Path]:
    """Yield metadata files under *paths*."""

    for p in paths:
        if p.is_dir():
            yield from (
                child
                for child in p.rglob("*")
                if child.is_file() and child.suffix.lower() in {".md", ".yml", ".yaml"}
            )
        else:
            yield p


def parse_args(argv: Sequence[str] | None = None) -> argparse.Namespace:
    parser = create_parser(
        "Rename 'gen-markdown-index' metadata keys to 'indextree'",
        log_default="log/update-indextree.txt",
    )
    parser.add_argument("paths", nargs="+", help="Files or directories to scan")
    return parser.parse_args(list(argv) if argv is not None else None)


def main(argv: Sequence[str] | None = None) -> int:
    args = parse_args(argv)
    configure_logging(args.verbose, args.log)
    paths = [Path(p) for p in args.paths]
    changes: list[str] = []
    checked = 0
    for fp in walk_files(paths):
        checked += 1
        try:
            changed = upgrade_file(fp)
        except Exception as exc:  # pragma: no cover - unexpected failures
            logger.warning("Failed to upgrade file", path=str(fp), error=str(exc))
            continue
        if changed:
            msg = f"{fp}: gen-markdown-index -> indextree"
            logger.info(msg)
            changes.append(msg)
    for msg in changes:
        print(msg)
    print(f"{checked} {'file' if checked == 1 else 'files'} checked")
    print(f"{len(changes)} {'file' if len(changes) == 1 else 'files'} changed")
    return 0


if __name__ == "__main__":  # pragma: no cover - manual execution
    raise SystemExit(main())

