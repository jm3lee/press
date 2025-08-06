"""Generate a Jinja list from an index JSON file."""

from __future__ import annotations

import argparse
from typing import Iterable, Mapping, List
import json

from pie.utils import add_file_logger, logger, read_json


def generate_lines(index: Mapping[str, Mapping[str, str]]) -> List[str]:
    """Return Jinja list items sorted by the ``name`` field."""
    lines: List[str] = []
    for _, item in sorted(index.items(), key=lambda p: p[1]["name"]):
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
        snippet = (
            "{{ " + json.dumps(desc, ensure_ascii=False) + " | link(style='title') }}"
        )
        lines.append(f"- {snippet}")
    return lines


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
