"""
This module scans a directory for Markdown (`.md`) and YAML (`.yml`/`.yaml`) files,
extracts metadata (YAML frontmatter in Markdown or full YAML content), computes
URLs for Markdown sources under `src/`, and builds a JSON index mapping each
document's `id` to its metadata (including generated URLs).
"""

import argparse
import glob
import json
import os
import sys
from typing import Any, Dict, Optional

import yaml
from pie.utils import add_file_logger, logger


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
        if ext.lower() in (".md", ".yml"):
            html_path = base + ".html"
            return "/" + html_path
    logger.warning("Can't create a url.", filename=filename)
    raise Exception("Can't create a url.")


def get_frontmatter(filename: str) -> Optional[Dict[str, Any]]:
    """Extract YAML frontmatter from a Markdown file.

    Args:
        filename: Path to the Markdown file.

    Returns:
        A dict of the frontmatter if present; otherwise `None`.
    """
    with open(filename, encoding="utf-8") as file:
        lines = file.readlines()

    if not lines or lines[0].strip() != "---":
        return None

    yaml_lines = []
    # Skip the first '---'
    for line in lines[1:]:
        if line.strip() == "---":
            break
        yaml_lines.append(line)

    content = "".join(yaml_lines)
    return yaml.safe_load(content)


def process_markdown(filepath: str) -> Optional[Dict[str, Any]]:
    """Load and prepare metadata from a Markdown file.

    Extracts YAML frontmatter and, if applicable, computes the URL for the
    Markdown document.

    Args:
        filepath: Path to the Markdown (`.md`) file.

    Returns:
        A metadata dict (including `url` if under `src/`) or `None` if
        frontmatter is missing.
    """
    metadata = get_frontmatter(filepath)
    if metadata is None:
        logger.warning("No frontmatter found in Markdown file", filename=filepath)
        return None
    metadata["url"] = get_url(filepath)
    return metadata


def process_yaml(filepath: str) -> Optional[Dict[str, Any]]:
    """
    Load and validate metadata from a YAML file.

    Parses the YAML file, auto-generates missing fields (`citation`, `id`),
    and computes the HTML URL if under `src/`.

    Args:
        filepath: Path to the YAML (`.yml`/`.yaml`) file.

    Returns:
        A metadata dict if parsing succeeds and content is a dict; otherwise
        `None`.
    """
    try:
        with open(filepath, encoding="utf-8") as yf:
            metadata = yaml.safe_load(yf)
            if "url" not in metadata:
                metadata["url"] = get_url(filepath)
            if "citation" not in metadata:
                # Intentionally use indexing so we get an exception here.
                # The name field must exist.
                metadata["citation"] = metadata["name"].lower()
            if "id" not in metadata:
                base, _ = os.path.splitext(filepath)
                metadata["id"] = base.split(os.sep)[-1]
            return metadata
    except yaml.YAMLError:
        logger.warning("Failed to parse YAML file", filename=filepath)
        raise


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


def build_index(source_dir: str, file_pattern: str = "**/*.md") -> Dict[str, Any]:
    """Build an index of document metadata from Markdown and YAML files.

    Scans `source_dir` recursively for files matching `file_pattern`. For
    Markdown files (`.md`), extracts YAML frontmatter and generates URLs for
    those under `src/`. For YAML files (`.yml`/`.yaml`), loads the entire file
    as metadata. Ensures each `id` is unique.

    Args:
        source_dir: Root directory to scan for files.
        file_pattern: Glob pattern (relative to `source_dir`) to select files.
            Defaults to `"**/*.md"`.

    Returns:
        A dict mapping each document `id` to its metadata (with added `url` for MD).

    Raises:
        KeyError: If duplicate `id` values are encountered.
    """
    index: Dict[str, Any] = {}
    pattern = os.path.join(source_dir, file_pattern)

    for filepath in glob.glob(pattern, recursive=True):
        _, ext = os.path.splitext(filepath)
        ext_lower = ext.lower()
        logger.debug("Processing file", filename=filepath)

        metadata: Optional[Dict[str, Any]] = None

        if ext_lower == ".md":
            metadata = process_markdown(filepath)
        elif ext_lower in (".yml", ".yaml"):
            metadata = process_yaml(filepath)
        else:
            # Skip files that are neither Markdown nor YAML
            continue

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
    parser.add_argument(
        "-l",
        "--log",
        help="Write logs to the specified file",
    )
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> None:
    """Build the index and write JSON output."""
    args = parse_args(argv)

    if args.log:
        add_file_logger(args.log, level="DEBUG")

    # Build index for Markdown and YAML separately
    md_index = build_index(args.source_dir, file_pattern="**/*.md")
    yaml_index = build_index(args.source_dir, file_pattern="**/*.yml")
    combined = {**md_index, **yaml_index}

    output_json = json.dumps(combined, ensure_ascii=False, indent=2)

    if args.output:
        with open(args.output, "w", encoding="utf-8") as outfile:
            outfile.write(output_json)
        logger.info("Index written to file", path=args.output)
    else:
        print(output_json)


if __name__ == "__main__":
    main()
