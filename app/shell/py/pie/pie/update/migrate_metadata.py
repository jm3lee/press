"""Move legacy metadata fields under ``doc`` and ``html.scripts``."""

from __future__ import annotations

import argparse
from io import StringIO
from pathlib import Path
from typing import Iterable, Sequence

from pie.cli import create_parser
from pie.logging import configure_logging, logger
from pie.yaml import YAML_EXTS, yaml, write_yaml

__all__ = ["main"]

FIELDS = ("author", "pubdate", "link", "title", "citation", "breadcrumbs")


def _migrate_mapping(data: dict) -> tuple[dict, bool]:
    """Move legacy fields into ``doc`` and ``html.scripts``."""
    changed = False
    doc = data.get("doc")
    if not isinstance(doc, dict):
        doc = {}
    else:
        doc = dict(doc)
    for field in FIELDS:
        if field in data:
            doc[field] = data.pop(field)
            changed = True
    if doc:
        if data.get("doc") != doc:
            data["doc"] = doc
            changed = True
    if "header_includes" in data:
        html = data.get("html")
        if not isinstance(html, dict):
            html = {}
        else:
            html = dict(html)
        scripts = html.get("scripts")
        if scripts is None:
            scripts = []
        else:
            scripts = list(scripts)
        header_includes = data.pop("header_includes")
        if not isinstance(header_includes, list):
            header_includes = [header_includes]
        scripts.extend(header_includes)
        if html.get("scripts") != scripts:
            html["scripts"] = scripts
            changed = True
        if data.get("html") != html:
            data["html"] = html
            changed = True
    return data, changed


def _migrate_yaml(path: Path) -> bool:
    data = yaml.load(path.read_text(encoding="utf-8")) or {}
    new_data, changed = _migrate_mapping(data)
    if changed:
        yaml.sort_keys = False
        write_yaml(new_data, path)
    return changed


def _migrate_markdown(path: Path) -> bool:
    lines = path.read_text(encoding="utf-8").splitlines(keepends=True)
    if not lines or not lines[0].startswith("---"):
        return False
    try:
        end = next(
            i for i, line in enumerate(lines[1:], start=1) if line.startswith("---")
        )
    except StopIteration:
        return False
    front = yaml.load("".join(lines[1:end])) or {}
    new_front, changed = _migrate_mapping(front)
    if changed:
        buf = StringIO()
        yaml.sort_keys = False
        yaml.dump(new_front, buf)
        new_front_lines = buf.getvalue().splitlines(keepends=True)
        path.write_text(
            "".join(["---\n", *new_front_lines, *lines[end:]]), encoding="utf-8"
        )
    return changed


def migrate_file(path: Path) -> bool:
    if path.suffix.lower() in YAML_EXTS:
        return _migrate_yaml(path)
    if path.suffix.lower() == ".md":
        return _migrate_markdown(path)
    return False


def walk_files(paths: Iterable[Path]) -> Iterable[Path]:
    for p in paths:
        if p.is_dir():
            yield from (
                child
                for child in p.rglob("*")
                if child.is_file() and child.suffix.lower() in {".md"} | YAML_EXTS
            )
        else:
            yield p


def parse_args(argv: Sequence[str] | None = None) -> argparse.Namespace:
    parser = create_parser(
        "Move top-level author/pubdate/link/title/citation/breadcrumbs fields "
        "under doc and header_includes under html.scripts",
        log_default="log/migrate-metadata.txt",
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
            updated = migrate_file(fp)
        except Exception as exc:  # pragma: no cover - unexpected failures
            logger.warning("Failed to migrate file", path=str(fp), error=str(exc))
            continue
        if updated:
            msg = f"{fp}: migrated"
            logger.info(msg)
            changes.append(msg)
    for msg in changes:
        print(msg)
    print(f"{checked} {'file' if checked == 1 else 'files'} checked")
    print(f"{len(changes)} {'file' if len(changes) == 1 else 'files'} changed")
    return 0


if __name__ == "__main__":  # pragma: no cover - manual execution
    raise SystemExit(main())
