"""Fill missing metadata fields in a YAML file after rendering Jinja."""

from __future__ import annotations

import argparse
import copy
import sys
from pathlib import Path
from typing import Iterable

from jinja2 import TemplateSyntaxError
from pie.cli import create_parser
from pie.filter.emojify import emojify_text
from pie.logging import configure_logging, logger
from pie.metadata import generate_missing_metadata
from pie.render import jinja as render_jinja
from pie.utils import write_yaml
from pie.yaml import yaml
from ruamel.yaml import YAMLError


def parse_args(argv: Iterable[str] | None = None) -> argparse.Namespace:
    """Parse command line arguments."""
    parser = create_parser("Generate missing metadata fields for YAML files")
    parser.add_argument(
        "paths",
        nargs="+",
        help="YAML files to update in place",
    )
    return parser.parse_args(list(argv) if argv is not None else None)


def _process_path(
    path: Path,
) -> tuple[dict | None, dict | None, str | None, str | None]:
    """Return metadata and intermediate values for ``path``."""
    if path.exists():
        text = path.read_text(encoding="utf-8")
        existing = yaml.load(text)
        metadata = copy.deepcopy(existing) if existing is not None else None
    else:
        existing = None
        text = None
        metadata = {}
    if metadata is not None:
        metadata = generate_missing_metadata(metadata, str(path))
    return metadata


def main(argv: Iterable[str] | None = None) -> None:
    """Entry point used by the ``process-yaml`` console script."""
    args = parse_args(argv)
    configure_logging(args.verbose, args.log)
    # ``render_jinja`` expects a mapping; default to an empty one.
    render_jinja.index_json = {}

    for path_str in args.paths:
        path = Path(path_str)
        metadata = _process_path(path)
        write_yaml(metadata, str(path))
        logger.debug("Processed YAML written", path=str(path))


if __name__ == "__main__":
    main()
