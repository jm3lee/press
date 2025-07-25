"""Generate a Markdown list from an index JSON file."""

from __future__ import annotations

import argparse
from typing import Iterable, Mapping, List

from xmera.utils import read_json


def generate_lines(index: Mapping[str, Mapping[str, str]]) -> List[str]:
    """Return Markdown list items sorted by the ``name`` field."""
    lines: List[str] = []
    for _, item in sorted(index.items(), key=lambda p: p[1]["name"]):
        name = item["name"]
        url = item["url"]
        icon = item.get("icon")
        if icon:
            lines.append(f"- [{icon} {name}]({url})")
        else:
            lines.append(f"- [{name}]({url})")
    return lines


def parse_args(argv: Iterable[str] | None = None) -> argparse.Namespace:
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        description="Generate a Markdown index from a JSON index file"
    )
    parser.add_argument("index", help="Path to index.json")
    return parser.parse_args(list(argv) if argv is not None else None)


def main(argv: Iterable[str] | None = None) -> None:
    """Entry point used by the ``gen-markdown-index`` console script."""
    args = parse_args(argv)
    index = read_json(args.index)
    for line in generate_lines(index):
        print(line)


if __name__ == "__main__":
    main()
