"""
This module scans a directory for Markdown (`.md`) and YAML (`.yml`/`.yaml`) files,
extracts metadata (YAML frontmatter in Markdown or full YAML content), computes
URLs for Markdown sources under `src/`, and builds a JSON index mapping each
document's `id` to its metadata (including generated URLs).
"""

import argparse
import json
import os
from typing import Any, Dict, Optional

from pie.metadata import read_from_markdown, read_from_yaml
from pie.logging import logger, add_log_argument, setup_file_logger


def get_url(filename: str) -> Optional[str]:
    """Compute the HTML URL for a given Markdown or YAML source file.

    Source files under `src/` map to HTML paths. For example::

        src/guide/intro.md         -> /guide/intro.html
        src/config/settings.yaml   -> /config/settings.html

    Args:
        filename: Path to the source file, expected to start with `src/`.

    Returns:
        A URL string starting with `/` and ending with `.html`, or `None`
        if the filename does not start with `src/` or has an unsupported
        extension.
    """
    prefix = "src" + os.sep
    if filename.startswith(prefix):
        relative_path = filename[len(prefix) :]
        base, ext = os.path.splitext(relative_path)
        if ext.lower() in (".md", ".yml", ".yaml"):
            html_path = base + ".html"
            return "/" + html_path
    logger.warning("Can't create a url.", filename=filename)
    raise Exception("Can't create a url.")




def validate_and_insert_metadata(
    metadata: Dict[str, Any],
    filepath: str,
    index: Dict[str, Any],
) -> None:
    """Validate and register a document's metadata into the index.

    Ensures the metadata contains a unique `id` field, logs warnings if missing,
    and raises on duplicates.

    Args:
        metadata: The document metadata to validate.
        filepath: The source file path (for logging).
        index: The global index mapping `id` to metadata.

    Raises:
        KeyError: If a duplicate `id` is detected.
    """
    doc_id = metadata.get("id")
    if doc_id:
        if doc_id in index:
            existing = index[doc_id]
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
    in ``extensions``. Markdown files (``.md``) have their YAML frontmatter
    extracted and URLs generated for those under ``src/``. YAML files
    (``.yml``/``.yaml``) are loaded entirely as metadata. Each document's
    ``id`` must be unique.

    Args:
        source_dir: Root directory to scan for files.
        extensions: Iterable of file extensions to include. Defaults to
            ``[".md", ".yml", ".yaml"]``.

    Returns:
        A dict mapping each document ``id`` to its metadata (with added ``url``
        for Markdown sources).

    Raises:
        KeyError: If duplicate ``id`` values are encountered.
    """
    if extensions is None:
        extensions = (".md", ".yml", ".yaml")

    index: Dict[str, Any] = {}

    for root, _, files in os.walk(source_dir):
        for name in files:
            _, ext = os.path.splitext(name)
            ext_lower = ext.lower()
            if ext_lower not in extensions:
                continue

            filepath = os.path.join(root, name)
            logger.debug("Processing file", filename=filepath)

            metadata: Optional[Dict[str, Any]] = None

            if ext_lower == ".md":
                metadata = read_from_markdown(filepath)
            elif ext_lower in (".yml", ".yaml"):
                metadata = read_from_yaml(filepath)

            if metadata:
                validate_and_insert_metadata(metadata, filepath, index)
                logger.debug("Processed file", filename=filepath)

    return index


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        description="Build a JSON index from Markdown/YAML files' metadata."
    )
    parser.add_argument(
        "source_dir",
        help="Root directory to scan for `.md`, `.yml`, and `.yaml` files",
    )
    parser.add_argument(
        "-o",
        "--output",
        help="Path to write the JSON index (defaults to stdout)",
    )
    add_log_argument(parser)
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> None:
    """Build the index and write JSON output."""
    args = parse_args(argv)

    setup_file_logger(args.log)

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
