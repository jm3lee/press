#!/usr/bin/env python3

"""Render Markdown text using the press Markdown renderer.

This module exposes the command line entry point for the
``render-press`` console script. Markdown input is rendered with
:func:`pie.render.jinja.render_press` and the resulting HTML is written to
the requested output file.
"""

from __future__ import annotations

import argparse
from pathlib import Path

from pie.cli import create_parser
from pie.logging import configure_logging
from pie.render.jinja import render_press
from pie.utils import read_utf8, write_utf8


__all__ = ["parse_args", "render_markdown", "main"]


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    """Return parsed arguments for the ``render-press`` CLI."""

    parser = create_parser("Render Markdown using the press renderer")
    parser.add_argument("markdown", help="Markdown source file")
    parser.add_argument("output", help="File to write rendered HTML to")
    return parser.parse_args(argv)


def render_markdown(markdown_path: str | Path) -> str:
    """Return HTML by rendering *markdown_path* with ``render_press``."""

    text = read_utf8(str(markdown_path))
    return str(render_press(text))


def main(argv: list[str] | None = None) -> None:
    """Entry point for the ``render-press`` console script."""

    args = parse_args(argv)
    configure_logging(args.verbose, args.log)
    html = render_markdown(args.markdown)
    write_utf8(html, args.output)


if __name__ == "__main__":
    main()
