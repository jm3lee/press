#!/usr/bin/env python3

"""Render a Markdown file inside a Jinja2 HTML template.

The module exposes :func:`render_page` and a small CLI used by the
``render-html`` console script. The Markdown source may include YAML front
matter which is merged into the Jinja context before rendering. Markdown is
converted using the :mod:`cmarkgfm` library which supports GitHub Flavored
Markdown, including tables, to match behaviour used across the press tooling.
"""

from __future__ import annotations

import argparse
import re
from pathlib import Path
from typing import Any, Mapping

import cmarkgfm

from pie.cli import create_parser
from pie.logging import configure_logging
from pie.utils import read_utf8, write_utf8
from pie.yaml import yaml, read_yaml as load_yaml_file
from .jinja import create_env, render_jinja

_front_matter_re = re.compile(r"^---\n(.*?)\n---\n(.*)", re.DOTALL)

env = create_env()

def _parse_markdown(path: str | Path) -> tuple[dict, str]:
    text = read_utf8(str(path))
    match = _front_matter_re.match(text)
    if match:
        meta_text, body = match.groups()
        metadata = yaml.load(meta_text) or {}
    else:
        metadata = {}
        body = text
    return metadata, body

def render_page(
    template_path: str | Path,
    markdown_path: str | Path,
    context: Mapping[str, Any] | None = None,
) -> str:
    """Return HTML by rendering *markdown_path* into *template*.

    Parameters
    ----------
    markdown_path:
        Path to the Markdown source file.
    template:
        Name of the Jinja template file.
    context:
        Optional mapping providing variables merged with any YAML metadata
        from the Markdown file.
    """
    metadata, md_text = _parse_markdown(markdown_path)
    ctx = dict(context or {})
    ctx.update(metadata)
    ctx['markdown_path'] = markdown_path
    tmpl = env.get_template(template_path)
    html_text = tmpl.render(**ctx)
    return html_text

def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    """Parse command line arguments."""
    parser = create_parser(
        "Render a Markdown file into an HTML template",
    )
    parser.add_argument("template_path", help="Jinja template file")
    parser.add_argument("markdown_path", help="Markdown source file")
    parser.add_argument("context")
    parser.add_argument("output")
    return parser.parse_args(argv)

def main(argv: list[str] | None = None) -> None:
    """Entry point for the ``render-html`` console script."""
    args = parse_args(argv)
    configure_logging(args.verbose, args.log)
    ctx = load_yaml_file(args.context) if args.context else {}
    rendered = render_page(args.template_path, args.markdown_path, ctx)
    write_utf8(rendered, args.output)

if __name__ == "__main__":
    main()
