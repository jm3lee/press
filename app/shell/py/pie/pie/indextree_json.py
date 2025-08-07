"""Generate JSON data for the React ``IndexTree`` component.

This module walks a directory tree of YAML metadata files in the same
fashion as the ``gen-markdown-index`` script and produces a nested data
structure describing the entries.  Each item exposes an ``id`` and
``label`` and, when links are enabled, copies the ``url`` from the
metadata verbatim.  Directories are represented by items containing a
``children`` list.
"""

from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
from typing import Any, Dict, Iterable, List, Tuple

import yaml

from pie.utils import add_file_logger


def _load_meta(path: Path) -> Dict[str, Any]:
    """Load YAML metadata from *path*."""

    with path.open("r", encoding="utf-8") as handle:
        return yaml.safe_load(handle) or {}


def _opt(meta: Dict[str, Any], key: str, default: bool = True) -> bool:
    """Return a boolean option from the ``gen-markdown-index`` section."""

    section = meta.get("gen-markdown-index") or {}
    return bool(section.get(key, default))


def _visit(directory: Path) -> Iterable[Tuple[Dict[str, Any], Path, bool]]:
    """Yield ``(meta, path, is_dir)`` tuples for *directory* entries."""

    for name in os.listdir(directory):
        p = directory / name
        if p.is_dir():
            index = p / "index.yml"
            if index.is_file():
                yield _load_meta(index), p, True
        elif p.is_file() and p.suffix == ".yml" and p.name != "index.yml":
            yield _load_meta(p), p, False


def scan_dir(root: Path) -> List[Dict[str, Any]]:
    """Return IndexTree nodes for *root* using ``gen-markdown-index`` rules."""

    nodes: List[Dict[str, Any]] = []
    for meta, path, is_dir in sorted(
        _visit(root), key=lambda x: str(x[0].get("title", "")).casefold()
    ):
        show = _opt(meta, "show")
        link = _opt(meta, "link")
        entry_id = meta.get("id")
        label = meta.get("title", entry_id)
        url = meta.get("url")

        if is_dir:
            children = scan_dir(path)
            if show:
                node: Dict[str, Any] = {"id": entry_id, "label": label}
                if link and url:
                    node["url"] = url
                if children:
                    node["children"] = children
                nodes.append(node)
            else:
                nodes.extend(children)
        else:
            if not show:
                continue
            node = {"id": entry_id, "label": label}
            if link and url:
                node["url"] = url
            nodes.append(node)

    return nodes


def parse_args(argv: Iterable[str] | None = None) -> argparse.Namespace:
    """Parse command line arguments."""

    parser = argparse.ArgumentParser(
        description="Generate IndexTree JSON from YAML metadata",
    )
    parser.add_argument("root", help="Root directory to scan")
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
    tree = scan_dir(Path(args.root))
    data = json.dumps(tree, indent=2, ensure_ascii=False)
    if args.outfile:
        Path(args.outfile).write_text(data + "\n", encoding="utf-8")
    else:
        print(data)


if __name__ == "__main__":  # pragma: no cover
    main()

