from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Iterator

from pie.cli import create_parser
from pie.logging import logger, configure_logging
from pie.metadata import load_metadata_pair

SUPPORTED_EXTS = {".md", ".yml", ".yaml"}

def scan_path(path: Path) -> Iterator[dict]:
    if path.is_dir():
        seen: set[Path] = set()
        for child in path.rglob("*"):
            if "node_modules" in child.parts:
                continue
            if child.is_file() and child.suffix in SUPPORTED_EXTS:
                base = child.with_suffix("")
                if base in seen:
                    continue
                seen.add(base)
                yield from scan_path(child)
    else:
        meta = load_metadata_pair(path)
        if not meta:
            return
        title = meta.get("title")
        url = meta.get("url")
        if not title or not url:
            logger.warning("Missing title or url", path=str(path))
            return
        entry = {"title": title, "url": url}
        section = meta.get("magicbar") or {}
        shortcut = section.get("shortcut")
        if shortcut:
            entry["shortcut"] = shortcut
        yield entry


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = create_parser("Generate MagicBar index")
    parser.add_argument("paths", nargs="+", help="Paths to scan")
    parser.add_argument(
        "-o",
        "--output",
        default="magicbar.json",
        help="Output JSON filename",
    )
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    if args.verbose or args.log:
        configure_logging(args.verbose, args.log)

    entries = []
    for p in args.paths:
        entries.extend(scan_path(Path(p)))
    entries.sort(key=lambda x: x["title"].lower())

    json_data = json.dumps(entries, indent=2)
    Path(args.output).write_text(json_data, encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
