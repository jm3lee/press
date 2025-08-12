"""Fill missing metadata fields in a YAML file."""

from __future__ import annotations

import argparse
import sys
from typing import Iterable

from pie.cli import create_parser
from pie.logging import logger, configure_logging
from pie.utils import write_yaml
from pie.metadata import read_from_yaml


def parse_args(argv: Iterable[str] | None = None) -> argparse.Namespace:
    """Parse command line arguments."""
    parser = create_parser("Generate missing metadata fields for a YAML file")
    parser.add_argument("input", help="Source YAML file")
    parser.add_argument("output", help="Destination file to write")
    return parser.parse_args(list(argv) if argv is not None else None)


def main(argv: Iterable[str] | None = None) -> None:
    """Entry point used by the ``process-yaml`` console script."""
    args = parse_args(argv)
    configure_logging(args.verbose, args.log)

    try:
        metadata = read_from_yaml(args.input)
    except Exception as exc:  # pragma: no cover - pass through message
        logger.error("Failed to process YAML", filename=args.input)
        raise SystemExit(1) from exc

    if metadata is None:
        logger.error("No metadata found", filename=args.input)
        sys.exit(1)

    write_yaml(metadata, args.output)

    logger.debug("Processed YAML written", path=args.output)


if __name__ == "__main__":
    main()
