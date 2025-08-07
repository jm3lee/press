"""Generate IndexTree JSON from a directory structure."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any, Dict, Iterable, List

from pie.utils import add_file_logger
from pie.update_index import load_index_from_path


def label_from(name: str) -> str:
    """Return a human readable label for *name*."""
    return name.replace("-", " ").title()


def scan_dir(root: Path, base: str) -> List[Dict[str, object]]:
    """Return IndexTree nodes for *root* using file metadata."""

    index, _ = load_index_from_path(root)

    base_prefix = base.rstrip("/")

    root_node: Dict[str, Any] = {"children": []}
    nodes: Dict[tuple[str, ...], Dict[str, Any]] = {(): root_node}

    def get_node(path: List[str]) -> Dict[str, Any]:
        key = tuple(path)
        if key not in nodes:
            parent = get_node(path[:-1])
            name = path[-1]
            node: Dict[str, Any] = {
                "id": name,
                "label": label_from(name),
                "url": f"{base_prefix}/{'/'.join(path)}",
            }
            parent.setdefault("children", []).append(node)
            nodes[key] = node
        return nodes[key]

    for metadata in index.values():
        url = metadata.get("url")
        if not url:
            continue
        parts = [p for p in url.lstrip("/").split("/") if p]
        if not parts:
            continue
        if parts == ["index.html"]:
            continue
        if parts[-1] == "index.html":
            segs = parts[:-1]
            node = get_node(segs)
            node["id"] = metadata.get("id", node["id"])
            node["label"] = metadata.get("title", node["label"])
            node["url"] = f"{base_prefix}{url}"
        else:
            parent = get_node(parts[:-1])
            stem = parts[-1].rsplit(".", 1)[0]
            parent.setdefault("children", []).append(
                {
                    "id": metadata.get("id", stem),
                    "label": metadata.get("title", label_from(stem)),
                    "url": f"{base_prefix}{url}",
                }
            )

    def sort(nodes: List[Dict[str, Any]]) -> None:
        nodes.sort(key=lambda n: str(n["label"]).casefold())
        for node in nodes:
            if "children" in node:
                sort(node["children"])

    children = root_node["children"]
    sort(children)
    return children


def parse_args(argv: Iterable[str] | None = None) -> argparse.Namespace:
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        description="Generate IndexTree JSON from a directory",
    )
    parser.add_argument("root", help="Root directory to scan")
    parser.add_argument(
        "--base-url",
        default="/",
        help="URL prefix for generated entries",
    )
    parser.add_argument(
        "-o",
        "--outfile",
        help="Write JSON output to this file",
    )
    parser.add_argument(
        "-l",
        "--log",
        help="Write debug logs to the specified file",
    )
    return parser.parse_args(list(argv) if argv is not None else None)


def main(argv: Iterable[str] | None = None) -> None:
    """Entry point for the ``indextree-json`` console script."""
    args = parse_args(argv)
    if args.log:
        add_file_logger(args.log, level="DEBUG")
    tree = scan_dir(Path(args.root), args.base_url.rstrip('/') + '/')
    data = json.dumps(tree, indent=2, ensure_ascii=False)
    if args.outfile:
        Path(args.outfile).write_text(data + "\n", encoding="utf-8")
    else:
        print(data)


if __name__ == "__main__":  # pragma: no cover
    main()
