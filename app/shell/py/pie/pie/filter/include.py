#!/usr/bin/env python3
"""Expand Python directives inside Markdown files.

The ``include-filter`` command reads a source Markdown document, executes any
fenced ``python`` code blocks, and writes the transformed output to another
file.  Available helper functions include ``include()`` for inserting other
Markdown files and ``mermaid()`` for converting Mermaid diagrams to images.

Links that end with ``.md`` are rewritten to ``.html`` so the output can be fed
directly to downstream rendering.  The command is primarily driven via
``preprocess`` and the
repository root ``makefile``.
"""

from __future__ import annotations

import argparse
import os
import re
import sys
from pathlib import Path
from typing import IO, Iterable, Callable

from pie.cli import create_parser
from pie.logging import logger, configure_logging
from pie.metadata import get_metadata_by_path
from pie.yaml import yaml

MD_LINK_PATTERN = re.compile(r"\[([^\]]+)\]\(([^)]+)\.md\)")

figcount = 0
heading_level = 0

outdir = None
infilename = None
outfilename = None
outfile = None
infile = None


def parse_metadata_or_print_first_line(f: IO[str]) -> dict | None:
    """Return YAML front matter from *f* or echo the first line.

    If the provided file object begins with a YAML front matter block delimited
    by ``---`` lines, the parsed dictionary is returned.  Otherwise the first
    line of the file is written unchanged to :data:`outfile` and ``None`` is
    returned.
    """

    for line in f:
        if line.strip() == "---":
            y = ""
            for line in f:
                if line.strip() == "---":
                    break
                y += line
            return yaml.load(y)
        print(line, end="", file=outfile)
        break


def _skip_front_matter(f: IO[str]) -> None:
    """Advance *f* past a YAML front matter block if present."""

    pos = f.tell()
    first = f.readline()
    if first.strip() == "---":
        for line in f:
            if line.strip() == "---":
                break
    else:
        f.seek(pos)


def include(filename: str) -> None:
    """Insert the contents of another Markdown file."""

    logger.info("include", filename=filename)
    with open(filename, "r", encoding="utf-8") as f:
        metadata = parse_metadata_or_print_first_line(f)
        if metadata and metadata.get("title"):
            print("#" * (heading_level + 1) + " " + metadata["title"], file=outfile)
        for line in f:
            if line.startswith("#"):
                line = "#" * heading_level + line
            print(line, end="", file=outfile)


def include_deflist_entry(
    *paths: str, glob: str = "*", sort_fn: Callable[[Iterable[Path]], Iterable[Path]] | None = None
) -> None:
    """Insert contents of Markdown files as definition list entries.

    Each argument in ``paths`` may be a file or directory.  Directories are
    scanned recursively for files matching ``glob``.  All discovered
    files are processed in alphabetical order by default, but a custom
    ``sort_fn`` can be supplied to override the ordering.
    """

    files: list[Path] = []
    for p in paths:
        path = Path(p)
        if path.is_dir():
            files.extend(f for f in path.rglob(glob) if f.is_file())
        else:
            files.append(path)

    if sort_fn is None:
        files = sorted(files, key=lambda p: p.name)
    else:
        files = list(sort_fn(files))

    for filename in files:
        logger.debug("include_deflist_entry", filename=str(filename))
        with open(filename, "r", encoding="utf-8") as f:
            rel = os.path.relpath(Path(filename).resolve(), Path.cwd())
            title = get_metadata_by_path(rel, "title")
            url = get_metadata_by_path(rel, "url")
            if title:
                if url:
                    cls = (
                        ""
                        if url.startswith(("http://", "https://"))
                        else ' class="internal-link"'
                    )
                    print(
                        f"<dt><a href=\"{url}\"{cls}>{title}</a></dt>",
                        file=outfile,
                    )
                else:
                    print(f"<dt>{title}</dt>", file=outfile)
            print("<dd>", file=outfile)
            _skip_front_matter(f)
            for line in f:
                print(line, end="", file=outfile)
            print("</dd>", file=outfile)


def yield_lines(infile: IO[str]) -> Iterable[str]:
    """Yield lines from *infile* until the next closing code fence."""

    for line in infile:
        if line.strip() == "```":
            break
        yield line


def execute_python_block(lines: Iterable[str]) -> None:
    """Execute a Python code block gathered from ``yield_lines``."""

    code = "".join(lines)
    exec(code, globals())


def new_filestem(stem: str) -> str:
    """Return *stem* with a numeric suffix that doesn't clash with existing files."""

    counter = 0
    while os.path.exists(f"{stem}{counter}.svg") or os.path.exists(
        f"{stem}{counter}.mmd"
    ):
        counter += 1
    return f"{stem}{counter}"


def mermaid(mmd_filename: str, alt_text: str, ref_id: str) -> None:
    """Convert a Mermaid diagram to an image and write a Markdown reference."""

    logger.info("Processing mermaid file", filename=mmd_filename)
    global figcount
    stem = new_filestem(f"{outdir}/diagram")
    with open(mmd_filename, "r", encoding="utf-8") as inmmd, open(
        f"{stem}.mmd", "w", encoding="utf-8"
    ) as outmmd:
        for line in inmmd:
            if line.strip() != "```mermaid":
                continue
            for line in inmmd:
                if line.strip() == "```":
                    break
                outmmd.write(line)
    os.system(f"npx mmdc -i {stem+'.mmd'} -o {stem+'.png'}")
    print(
        f'![{alt_text}](./{os.path.basename(stem+".png")}){{ {ref_id} }}',
        file=outfile,
    )
    figcount += 1


def md_to_html_links(line: str) -> str:
    """Replace ``.md`` links in *line* with ``.html`` versions."""

    return MD_LINK_PATTERN.sub(r"[\1](\2.html)", line)


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    """Parse command line arguments."""

    parser = create_parser("Expand Python directives inside a Markdown file")
    parser.add_argument("outdir", help="Output directory for diagrams")
    parser.add_argument("infile", help="Input Markdown file")
    parser.add_argument("outfile", help="Output Markdown file")
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> None:
    """Process a Markdown file and expand custom directives.

    ``include-filter`` is primarily used by the build scripts.  It executes any
    ``python`` fenced blocks in the input and writes the resulting Markdown to
    ``outfile``.  Links ending in ``.md`` are rewritten so the renderer can
    convert the file directly to HTML.
    """

    global outdir, infilename, outfilename, infile, outfile, heading_level

    args = parse_args(argv)

    configure_logging(args.verbose, args.log)

    outdir = args.outdir
    infilename = args.infile
    outfilename = args.outfile

    with open(infilename, "r", encoding="utf-8") as infile, open(
        outfilename, "w", encoding="utf-8"
    ) as outfile:
        for line in infile:
            if line.strip() == "```python":
                execute_python_block(yield_lines(infile))
            else:
                if line.startswith("#"):
                    parts = line.split(" ")
                    heading_level = len(parts[0])
                line = md_to_html_links(line)
                print(line, end="", file=outfile)


if __name__ == "__main__":
    main()
