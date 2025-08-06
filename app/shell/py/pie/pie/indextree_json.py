"""Generate IndexTree JSON from a directory structure."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any, Dict, Iterable, List

from pie.utils import add_file_logger, logger
from pie.load_metadata import load_metadata_pair


def title_from(name: str) -> str:
    """Return a human readable title for *name*."""
    return name.replace("-", " ").title()


def scan_dir(root: Path, base: str) -> List[Dict[str, object]]:
    """Return IndexTree nodes for *root* using file metadata."""

    nodes: List[Dict[str, object]] = []
    for child in sorted(root.iterdir(), key=lambda p: p.name):
        if child.name.startswith('.'):
            continue

        if child.is_dir():
            metadata = None
            for ext in (".md", ".yml", ".yaml"):
                index_file = child / f"index{ext}"
                if index_file.exists():
                    try:
                        metadata = load_metadata_pair(index_file)
                    except Exception:  # pragma: no cover - fall back
                        metadata = None
                    break

            node_id = metadata.get("id") if metadata else child.name
            title = metadata.get("title") if metadata else title_from(child.name)
            url = metadata.get("url") if metadata else f"{base}{child.name}"

            node: Dict[str, Any] = {
                "id": node_id,
                "title": title,
                "url": url,
            }
            children = scan_dir(child, f"{base}{child.name}/")
            if children:
                node["children"] = children
            nodes.append(node)
        elif child.is_file():
            if child.name in {"index.md", "index.yml", "index.yaml"}:
                continue

            if child.suffix.lower() not in {".md", ".yml", ".yaml"}:
                continue

            try:
                metadata = load_metadata_pair(child)
            except Exception:  # pragma: no cover - fall back
                metadata = None

            if not metadata:
                continue

            stem = child.stem
            node_id = metadata.get("id", stem)
            title = metadata.get("title", title_from(stem))
            url = metadata.get("url", f"{base}{stem}")

            nodes.append({"id": node_id, "title": title, "url": url})

    return nodes


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
