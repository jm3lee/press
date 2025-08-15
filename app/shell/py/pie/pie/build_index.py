"""
This module scans a directory for Markdown (`.md`) and YAML (`.yml`/`.yaml`) files,
extracts metadata (YAML frontmatter in Markdown or full YAML content), computes
URLs for Markdown sources under `src/`, and builds a JSON index mapping each
document's `id` to its metadata (including generated URLs).
"""

import argparse
import json
import os
from pathlib import Path
from typing import Any, Dict

from pie.cli import create_parser
from pie.logging import logger, add_log_argument, configure_logging
from pie.metadata import load_metadata_pair


## Functions for reading metadata are provided by ``pie.metadata``.


def validate_and_insert_metadata(filepath: str, index: Dict[str, Any]) -> None:
    """Load metadata from ``filepath`` and register it into the index.

    The metadata for ``filepath`` and any sibling Markdown/YAML file is loaded
    via :func:`load_metadata_pair`. A document's ``id`` must be unique within
    ``index``. If the same ``id`` is encountered again from the same pair of
    files, the duplicate is ignored. A ``KeyError`` is raised for conflicting
    ``id`` values originating from different paths.

    Args:
        filepath: The source file path.
        index: The global index mapping ``id`` to metadata.

    Raises:
        KeyError: If a duplicate ``id`` is detected from a different file.
    """
    metadata = load_metadata_pair(Path(filepath))
    if not metadata:
        return

    doc_id = metadata.get("id")
    if doc_id:
        existing = index.get(doc_id)
        if existing:
            if existing.get("path") == metadata.get("path"):
                return
            raise KeyError(
                f"Duplicate id found: '{doc_id}'. "
                f"Existing: {existing}, New: {metadata}"
            )
        index[doc_id] = metadata
    else:
        title = metadata.get("title", "<unknown>")
        logger.warning(
            "Missing 'id' field in metadata",
            title=title,
            filename=filepath,
        )


def build_index(
    source_dir: str, extensions: list[str] | tuple[str, ...] | None = None
) -> Dict[str, Any]:
    """Build an index of document metadata from Markdown and YAML files.

    Scans ``source_dir`` recursively and processes any files whose extension is
    in ``extensions``. Metadata is loaded using :func:`load_metadata_pair` and
    inserted into ``index`` if the document ``id`` is unique.

    Args:
        source_dir: Root directory to scan for files.
        extensions: Iterable of file extensions to include. Defaults to
            ``[".md", ".yml", ".yaml"]``.

    Returns:
        A dict mapping each document ``id`` to its metadata.

    Raises:
        KeyError: If duplicate ``id`` values are encountered.
    """
    if extensions is None:
        extensions = (".md", ".yml", ".yaml")

    index: Dict[str, Any] = {}

    for root, _, files in os.walk(source_dir):
        for name in files:
            _, ext = os.path.splitext(name)
            if ext.lower() not in extensions:
                continue

            filepath = os.path.join(root, name)
            logger.debug("Processing file", filename=filepath)

            validate_and_insert_metadata(filepath, index)
            logger.debug("Processed file", filename=filepath)

    return index


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    """Parse command line arguments."""
    parser = create_parser("Build a JSON index from Markdown/YAML files' metadata.")
    parser.add_argument(
        "source_dir",
        help="Root directory to scan for `.md`, `.yml`, and `.yaml` files",
    )
    parser.add_argument(
        "-o",
        "--output",
        help="Path to write the JSON index (defaults to stdout)",
    )
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> None:
    """Build the index and write JSON output."""
    args = parse_args(argv)

    configure_logging(args.verbose, args.log)

    index = build_index(args.source_dir)

    output_json = json.dumps(index, ensure_ascii=False, indent=2)

    if args.output:
        with open(args.output, "w", encoding="utf-8") as outfile:
            outfile.write(output_json)
        logger.info("Index written to file", path=args.output)
    else:
        print(output_json)


if __name__ == "__main__":
    main()
