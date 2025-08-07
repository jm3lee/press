#!/usr/bin/env python3

import json
import os
import warnings
from pathlib import Path

import yaml
from pie.load_metadata import load_metadata_pair


def getopt_link(meta):
    if meta.get("gen-markdown-index"):
        return meta.get("gen-markdown-index").get("link", True)
    return True


def getopt_show(meta):
    if meta.get("gen-markdown-index"):
        return meta.get("gen-markdown-index").get("show", True)
    return True


def visit(directory):
    for filename in os.listdir(directory):
        try:
            p = os.path.join(directory, filename)
            if os.path.isdir(p):
                if os.path.isfile(os.path.join(p, "index.yml")):
                    meta = load_metadata_pair(Path(os.path.join(p, "index.yml")))
                    yield (
                        meta["id"],
                        meta["title"],
                        meta.get("url"),
                        p,
                        getopt_link(meta),
                        getopt_show(meta),
                    )
            elif os.path.isfile(p) and p.endswith(".yml") and filename != "index.yml":
                meta = load_metadata_pair(Path(p))
                yield (
                    meta["id"],
                    meta["title"],
                    meta.get("url"),
                    p,
                    getopt_link(meta),
                    getopt_show(meta),
                )
        except Exception as e:
            warnings.warn(f"Failed to process {p}")
            raise


def process_dir(directory):
    """
    Recursively process a directory tree to print structured link entries.

    Args:
        directory (str): Path to the current directory.
    """
    for entry in sorted(list(visit(directory)), key=lambda x: x[1].lower()):
        entry_id = entry[0]
        entry_title = entry[1]
        entry_url = entry[2]
        entry_path = entry[3]
        entry_link = entry[4]
        entry_show = entry[5]
        if os.path.isdir(entry_path):
            if entry_show:
                if entry_link:
                    yield {
                        "id": entry_id,
                        "label": entry_title,
                        "url": entry_url,
                        "children": list(process_dir(entry_path)),
                    }
                else:
                    yield {
                        "id": entry_id,
                        "label": entry_title,
                        "children": list(process_dir(entry_path)),
                    }
            else:
                process_dir(entry_path)
                yield from process_dir(entry_path)
        else:
            if entry_show:
                if entry_link:
                    yield {"id": entry_id, "label": entry_title, "url": entry_url}
                else:
                    yield {"id": entry_id, "label": entry_title}


def main():
    import sys

    root_dir = sys.argv[1] if len(sys.argv) > 1 else "."
    data = list(process_dir(root_dir))
    print(json.dumps(data, indent=2))


if __name__ == "__main__":
    main()
