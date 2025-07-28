"""Generate a Jinja list from an index JSON file."""

from __future__ import annotations

import argparse
from typing import Iterable, Mapping, List, Dict, Any
import json

from xmera.utils import read_json
from pie.utils import add_file_logger, logger


def _parse_segments(url: str) -> List[str]:
    """Return path segments for an internal URL."""
    if not url.startswith("/"):
        return []
    path = url.lstrip("/")
    if path.endswith(".html"):
        path = path[:-5]
    parts = path.split("/")
    if parts and parts[-1] == "index":
        parts = parts[:-1]
    return parts


def _common_prefix(lists: List[List[str]]) -> List[str]:
    """Return the common path prefix for all lists."""
    if not lists:
        return []
    prefix = lists[0]
    for lst in lists[1:]:
        i = 0
        while i < len(prefix) and i < len(lst) and prefix[i] == lst[i]:
            i += 1
        prefix = prefix[:i]
        if not prefix:
            break
    return prefix


def _add_to_tree(tree: Dict[str, Any], parts: List[str], item: Mapping[str, Any]) -> None:
    node = tree
    for part in parts:
        node = node.setdefault("_children", {}).setdefault(part, {"_item": None, "_children": {}})
    node["_item"] = item


def _build_tree(index: Mapping[str, Mapping[str, Any]]) -> Dict[str, Any]:
    entries: List[tuple[List[str], Mapping[str, Any]]] = []
    internal_paths: List[List[str]] = []
    for item in index.values():
        parts = _parse_segments(item.get("url", ""))
        entries.append((parts, item))
        if parts:
            internal_paths.append(parts)

    prefix = _common_prefix(internal_paths)

    tree: Dict[str, Any] = {"_item": None, "_children": {}}
    for parts, item in entries:
        rel_parts = parts[len(prefix) :] if parts[: len(prefix)] == prefix else parts
        _add_to_tree(tree, rel_parts, item)

    return tree


def _desc_from_item(item: Mapping[str, Any]) -> Dict[str, Any]:
    desc = {
        "citation": item["name"],
        "url": item["url"],
    }
    icon = item.get("icon")
    if icon is not None:
        desc["icon"] = icon
    link = item.get("link")
    if isinstance(link, dict) and "tracking" in link:
        desc["link"] = {"tracking": link["tracking"]}
    return desc


def _generate_from_tree(tree: Dict[str, Any], indent: int = 0, include_self: bool = False) -> List[str]:
    lines: List[str] = []
    if include_self and tree.get("_item"):
        desc = _desc_from_item(tree["_item"])
        snippet = "{{ " + json.dumps(desc, ensure_ascii=False) + " | linktitle }}"
        lines.append(f"{'  ' * indent}- {snippet}")

    children = tree.get("_children", {})
    def sort_key(item):
        node = item[1]
        meta = node.get("_item")
        if meta is not None:
            return meta.get("name", "")
        return item[0]

    for key, child in sorted(children.items(), key=sort_key):
        meta = child.get("_item")
        if meta is not None:
            desc = _desc_from_item(meta)
            snippet = "{{ " + json.dumps(desc, ensure_ascii=False) + " | linktitle }}"
            lines.append(f"{'  ' * indent}- {snippet}")
        else:
            lines.append(f"{'  ' * indent}- {key}")
        lines.extend(_generate_from_tree(child, indent + 1, include_self=False))
    return lines


def generate_lines(index: Mapping[str, Mapping[str, Any]]) -> List[str]:
    """Return Jinja list items mirroring the directory structure."""
    tree = _build_tree(index)
    return _generate_from_tree(tree, include_self=True)


def parse_args(argv: Iterable[str] | None = None) -> argparse.Namespace:
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        description="Generate a Markdown index from a JSON index file"
    )
    parser.add_argument("index", help="Path to index.json")
    parser.add_argument(
        "-l",
        "--log",
        help="Write logs to the specified file",
    )
    return parser.parse_args(list(argv) if argv is not None else None)


def main(argv: Iterable[str] | None = None) -> None:
    """Entry point used by the ``gen-markdown-index`` console script."""
    args = parse_args(argv)
    if args.log:
        add_file_logger(args.log, level="DEBUG")
    index = read_json(args.index)
    for line in generate_lines(index):
        print(line)


if __name__ == "__main__":
    main()
