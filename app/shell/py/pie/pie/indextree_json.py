#!/usr/bin/env python3

import argparse
import json
from pathlib import Path

from pie.cli import create_parser
from pie.logging import logger, configure_logging

from pie.index_tree import walk, getopt_link, getopt_show


def process_dir(directory: Path):
    """Recursively process *directory* to yield structured entries."""
    entries = list(walk(directory))
    for meta, path in entries:
        if "title" not in meta:
            raise ValueError(f"Missing 'title' in {path}")
    entries.sort(key=lambda x: x[0]["title"].lower())
    for meta, path in entries:
        entry_id = meta["id"]
        entry_title = meta["title"]
        entry_url = meta.get("url")
        entry_link = getopt_link(meta)
        entry_show = getopt_show(meta)
        if path.is_dir():
            children = list(process_dir(path))
            if entry_show:
                node = {"id": entry_id, "label": entry_title, "children": children}
                if entry_link and entry_url:
                    node["url"] = entry_url
                yield node
            else:
                yield from children
        else:
            if entry_show:
                node = {"id": entry_id, "label": entry_title}
                if entry_link and entry_url:
                    node["url"] = entry_url
                yield node


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = create_parser("Generate JSON index from metadata tree")
    parser.add_argument("root", nargs="?", default=".", help="Directory to scan")
    parser.add_argument("output", nargs="?", help="Write JSON to file")
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    if args.verbose or args.log:
        configure_logging(args.verbose, args.log)

    root_dir = Path(args.root)
    try:
        data = list(process_dir(root_dir))
    except ValueError as exc:
        logger.error(str(exc))
        raise SystemExit(1)

    json_data = json.dumps(data, indent=2)
    if args.output:
        Path(args.output).write_text(json_data, encoding="utf-8")
    else:
        print(json_data)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
