#!/usr/bin/env python3

import json
from pathlib import Path

from pie.logging import logger

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


def main():
    import sys

    root_dir = Path(sys.argv[1]) if len(sys.argv) > 1 else Path(".")
    try:
        data = list(process_dir(root_dir))
    except ValueError as exc:
        logger.error(str(exc))
        sys.exit(1)
    print(json.dumps(data, indent=2))


if __name__ == "__main__":
    main()
