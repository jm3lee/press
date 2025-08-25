#!/usr/bin/env python3

import argparse
import json
from pathlib import Path
from typing import Iterator

from pie.cli import create_parser
from pie.logging import logger, configure_logging

from pie.index_tree import walk, getopt_link, getopt_show, sort_entries


def process_dir(directory: Path, tag: str | None = None) -> Iterator[dict]:
    """Recursively process *directory* to yield structured entries.

    If *tag* is provided, only entries whose ``tags`` metadata contains the
    exact string are included. Directories are kept when they match or have
    matching descendants.
    """
    logger.debug("Scanning directory", directory=directory)
    entries = list(walk(directory))
    for meta, path in entries:
        if "title" not in meta:
            raise ValueError(f"Missing 'title' in {path}")
    sort_entries(entries)
    for meta, path in entries:
        entry_id = meta["id"]
        entry_title = meta["title"]
        entry_url = meta.get("url")
        entry_link = getopt_link(meta)
        entry_show = getopt_show(meta)
        tags = meta.get("tags") or []
        include_current = tag is None or tag in tags
        if tag:
            if include_current:
                logger.debug(
                    "Tag matched", tag=tag, path=path, tags=tags
                )
            else:
                logger.debug(
                    "Tag did not match", tag=tag, path=path, tags=tags
                )
        else:
            logger.debug("Processing", path=path, tags=tags)
        if path.is_dir():
            logger.debug("Descending into directory", path=path)
            children = list(process_dir(path, tag))
            if entry_show and (include_current or children):
                node: dict[str, object] = {"id": entry_id, "label": entry_title}
                if children:
                    node["children"] = children
                if entry_link and entry_url:
                    node["url"] = entry_url
                yield node
            else:
                yield from children
        else:
            if entry_show and include_current:
                node = {"id": entry_id, "label": entry_title}
                if entry_link and entry_url:
                    node["url"] = entry_url
                yield node


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = create_parser("Generate JSON index from metadata tree")
    parser.add_argument("root", nargs="?", default=".", help="Directory to scan")
    parser.add_argument("output", nargs="?", help="Write JSON to file")
    parser.add_argument(
        "-t", "--tag", metavar="TAG", help="Only include entries with this tag"
    )
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    if args.verbose or args.log:
        configure_logging(args.verbose, args.log)

    root_dir = Path(args.root)
    try:
        data = list(process_dir(root_dir, args.tag))
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
