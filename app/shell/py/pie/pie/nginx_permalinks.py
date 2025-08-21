#!/usr/bin/env python3
"""Generate Nginx redirect rules from metadata permalinks."""

from __future__ import annotations

import argparse
import os
from typing import Iterable, Sequence

from pathlib import Path

from pie.cli import create_parser
from pie.logging import logger, configure_logging
from pie.metadata import (
    get_metadata_by_path,
    build_from_redis,
    load_metadata_pair,
)


def _load_metadata(filepath: str) -> dict | None:
    """Load metadata for *filepath* from Redis or fall back to the file pair."""
    try:
        doc_id = get_metadata_by_path(filepath, "id")
        if doc_id:
            meta = build_from_redis(f"{doc_id}.") or {}
            if "id" not in meta:
                meta["id"] = doc_id
            logger.debug("Loaded metadata from redis", path=filepath, id=doc_id)
            return meta
        logger.debug("No doc_id found in redis", path=filepath)
    except Exception:
        logger.debug("Redis lookup failed", path=filepath, exc_info=True)

    logger.debug("Falling back to load_metadata_pair", path=filepath)
    try:
        return load_metadata_pair(Path(filepath))
    except Exception:
        logger.warning("Failed to load metadata", path=filepath, exc_info=True)
        return None


def collect_redirects(source_dir: str) -> list[tuple[str, str]]:
    """Return ``(permalink, url)`` pairs for metadata under *source_dir*."""
    redirects: list[tuple[str, str]] = []
    seen: set[tuple[str, str]] = set()
    for root, _, files in os.walk(source_dir):
        for name in files:
            base, ext = os.path.splitext(name)
            ext = ext.lower()
            if ext not in {".md", ".yml", ".yaml"}:
                continue
            filepath = os.path.join(root, name)
            logger.debug("Processing file", path=filepath)
            meta = _load_metadata(filepath)
            if not meta:
                continue
            permalink = meta.get("permalink")
            url = meta.get("url")
            if permalink and url:
                if isinstance(permalink, str):
                    links: Iterable[str] = [permalink]
                else:
                    links = permalink
                for link in links:
                    pair = (str(link), str(url))
                    if pair not in seen:
                        redirects.append(pair)
                        seen.add(pair)
                        logger.debug("Added redirect", src=link, dest=url)
    logger.debug("Collected redirects", count=len(redirects))
    return redirects


def format_redirects(redirects: list[tuple[str, str]]) -> str:
    """Format redirects as Nginx ``location`` blocks."""
    lines: list[str] = []
    for src, dest in redirects:
        if not src.startswith("/"):
            src = "/" + src
        if not dest.startswith("/"):
            dest = "/" + dest
        block = f"location = {src} {{\n    return 301 {dest};\n}}"
        lines.append(block)
    return "\n".join(lines) + ("\n" if lines else "")


def parse_args(argv: Sequence[str] | None = None) -> argparse.Namespace:
    """Parse command line arguments."""
    parser = create_parser(
        "Generate Nginx redirects from metadata permalinks",
        log_default="log/nginx-permalinks.txt",
    )
    parser.add_argument("source_dir", help="Directory to scan for metadata files")
    parser.add_argument("-o", "--output", help="Path to write Nginx config")
    return parser.parse_args(list(argv) if argv is not None else None)


def main(argv: Sequence[str] | None = None) -> None:
    """Entry point for ``nginx-permalinks`` console script."""
    args = parse_args(argv)
    if args.log:
        os.makedirs(os.path.dirname(args.log), exist_ok=True)
    configure_logging(args.verbose, args.log)
    redirects = collect_redirects(args.source_dir)
    output = format_redirects(redirects)
    if args.output:
        with open(args.output, "w", encoding="utf-8") as fh:
            fh.write(output)
        logger.info("Redirects written", path=args.output)
    else:
        print(output, end="")

    logger.info("Generated redirects", count=len(redirects))


if __name__ == "__main__":  # pragma: no cover - manual execution
    main()
