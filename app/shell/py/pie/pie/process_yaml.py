"""Fill missing metadata fields in a YAML file."""

from __future__ import annotations

import argparse
import sys
from typing import Iterable

from pie.cli import create_parser
from pie.filter.emojify import emojify_text
from pie.logging import logger, configure_logging
from pie.utils import write_yaml
from pie.metadata import generate_missing_metadata, read_from_yaml


def parse_args(argv: Iterable[str] | None = None) -> argparse.Namespace:
    """Parse command line arguments."""
    parser = create_parser("Generate missing metadata fields for YAML files")
    parser.add_argument(
        "paths",
        nargs="+",
        help="YAML files to update in place",
    )
    return parser.parse_args(list(argv) if argv is not None else None)


def _emojify(value):
    """Recursively replace ``:emoji:`` codes in ``value``."""
    if isinstance(value, dict):
        return {k: _emojify(v) for k, v in value.items()}
    if isinstance(value, list):
        return [_emojify(v) for v in value]
    if isinstance(value, str):
        return emojify_text(value)
    return value


def main(argv: Iterable[str] | None = None) -> None:
    """Entry point used by the ``process-yaml`` console script."""
    args = parse_args(argv)
    configure_logging(args.verbose, args.log)

    for path in args.paths:
        try:
            metadata = read_from_yaml(path)
            if metadata is not None:
                metadata = generate_missing_metadata(metadata, path)
                metadata = _emojify(metadata)
        except Exception as exc:  # pragma: no cover - pass through message
            logger.error("Failed to process YAML", filename=path)
            raise SystemExit(1) from exc

        if metadata is None:
            logger.error("No metadata found", filename=path)
            sys.exit(1)

        write_yaml(metadata, path)
        logger.debug("Processed YAML written", path=path)


if __name__ == "__main__":
    main()
