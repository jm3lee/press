#!/usr/bin/env python3
"""Generate a Markdown list from an index JSON file."""

import argparse
import json
from typing import Dict, Any


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Generate a Markdown index from build index JSON",
    )
    parser.add_argument(
        "index_json",
        help="Path to index.json produced by build-index",
    )
    return parser.parse_args(argv)


def load_index(path: str) -> Dict[str, Any]:
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def emit_markdown(index: Dict[str, Any]) -> None:
    for key in sorted(index.keys()):
        meta = index[key]
        title = meta.get("title") or meta.get("name", key)
        url = meta.get("url", "#")
        print(f"- [{title}]({url})")


def main(argv: list[str] | None = None) -> None:
    args = parse_args(argv)
    data = load_index(args.index_json)
    emit_markdown(data)


if __name__ == "__main__":
    main()
