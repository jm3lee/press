#!/usr/bin/env python3
"""Generate a Markdown index from YAML metadata files."""

from __future__ import annotations

import argparse
import warnings
from pathlib import Path
from typing import Iterator

import yaml


def extract_metadata(filepath: Path) -> dict | None:
    """Return parsed YAML metadata for *filepath* or ``None`` if invalid."""
    try:
        with filepath.open("r", encoding="utf-8") as f:
            return yaml.safe_load(f) or {}
    except Exception as e:  # pragma: no cover - warning path
        warnings.warn(f"Invalid YAML: {filepath} ({e})")
        return None


def getopt_link(meta: dict) -> bool:
    """Return whether the item should be linked."""
    section = meta.get("gen-markdown-index") or {}
    return section.get("link", True)


def getopt_show(meta: dict) -> bool:
    """Return whether the item should be shown."""
    section = meta.get("gen-markdown-index") or {}
    return section.get("show", True)


def visit(directory: Path) -> Iterator[tuple[str, str, Path, bool, bool]]:
    """Yield metadata tuples for entries in *directory*."""
    for path in directory.iterdir():
        try:
            if path.is_dir():
                index_file = path / "index.yml"
                if index_file.is_file():
                    meta = extract_metadata(index_file)
                    if meta:
                        yield (
                            meta["id"],
                            meta["title"],
                            path,
                            getopt_link(meta),
                            getopt_show(meta),
                        )
            elif path.is_file() and path.suffix == ".yml" and path.name != "index.yml":
                meta = extract_metadata(path)
                if meta:
                    yield (
                        meta["id"],
                        meta["title"],
                        path,
                        getopt_link(meta),
                        getopt_show(meta),
                    )
        except Exception as e:  # pragma: no cover - warning path
            warnings.warn(f"Failed to process {path}")
            raise


def generate(directory: Path, level: int = 0) -> Iterator[str]:
    """Yield Markdown list items for *directory* recursively."""
    for entry in sorted(visit(directory), key=lambda x: x[1].lower()):
        entry_id, title, path, link, show = entry
        if show:
            if link:
                yield "  " * level + f'- {{{{"{entry_id}"|linktitle}}}}'
            else:
                yield "  " * level + f"- {{{{'{title}'|title}}}}"
        if path.is_dir():
            if show:
                yield from generate(path, level + 1)
            else:
                yield from generate(path, level)


def main(argv: list[str] | None = None) -> None:
    """Entry point for the ``gen-markdown-index`` console script."""
    parser = argparse.ArgumentParser(description="Generate a Markdown index")
    parser.add_argument("root_dir", nargs="?", default=".", help="Root directory to scan")
    args = parser.parse_args(argv)
    for line in generate(Path(args.root_dir)):
        print(line)


if __name__ == "__main__":  # pragma: no cover - manual execution
    main()
