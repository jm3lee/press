#!/usr/bin/env python3
"""Generate ``sitemap.xml`` from HTML files."""

from __future__ import annotations

import argparse
import os
from pathlib import Path
from typing import Sequence

from pie.cli import create_parser
from pie.logging import configure_logging, logger
from pie.utils import ExcludeList, load_exclude_file


DEFAULT_EXCLUDE = Path("cfg/sitemap-exclude.yml")


def generate(
    build_dir: Path, base_url: str, exclude: ExcludeList | None = None
) -> list[str]:
    """Return sitemap entries for *build_dir* using *base_url*.

    ``exclude`` contains paths, wildcards, or regular expressions that are
    omitted from the sitemap.
    """

    skip = exclude or ExcludeList([], build_dir)
    base = base_url.rstrip("/")
    entries: list[str] = []
    for path in sorted(build_dir.rglob("*.html")):
        if path in skip:
            continue
        rel_path = path.relative_to(build_dir)
        rel = rel_path.as_posix()
        url = f"{base}/{rel}"
        if path.name == "index.html":
            rel_dir = rel_path.parent.as_posix()
            rel_dir = "" if rel_dir == "." else rel_dir
            url = f"{base}/{rel_dir}" if rel_dir else base
            if not url.endswith("/"):
                url += "/"
        entries.append(url)
    lines = [
        "<?xml version=\"1.0\" encoding=\"UTF-8\"?>",
        '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">',
    ]
    lines.extend(f"  <url><loc>{u}</loc></url>" for u in entries)
    lines.append("</urlset>")
    output = build_dir / "sitemap.xml"
    output.write_text("\n".join(lines) + "\n", encoding="utf-8")
    logger.info("Wrote sitemap", path=str(output), count=len(entries))
    return entries


def parse_args(argv: Sequence[str] | None = None) -> argparse.Namespace:
    """Parse command line arguments."""

    parser = create_parser("Generate sitemap.xml from HTML files")
    parser.add_argument(
        "directory",
        nargs="?",
        default="build",
        help="Directory containing HTML files",
    )
    parser.add_argument(
        "-x",
        "--exclude",
        help="YAML file listing HTML files to skip",
    )
    parser.add_argument(
        "base_url",
        nargs="?",
        help="Base URL for absolute links",
    )
    return parser.parse_args(list(argv) if argv is not None else None)


def main(argv: Sequence[str] | None = None) -> int:
    """Entry point for the ``sitemap`` console script."""

    args = parse_args(argv)
    base_url = args.base_url or os.environ.get("BASE_URL")
    if not base_url:
        raise SystemExit("BASE_URL must be provided")
    configure_logging(args.verbose, args.log)
    build_dir = Path(args.directory)
    if args.exclude:
        exclude_file = args.exclude
    elif DEFAULT_EXCLUDE.is_file():
        exclude_file = DEFAULT_EXCLUDE
    else:
        exclude_file = None
    exclude = load_exclude_file(exclude_file, build_dir)
    generate(build_dir, base_url, exclude)
    return 0


if __name__ == "__main__":  # pragma: no cover - manual execution
    raise SystemExit(main())

