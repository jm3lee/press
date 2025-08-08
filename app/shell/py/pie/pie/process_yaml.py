"""Fill missing metadata fields in a YAML file."""

from __future__ import annotations

import argparse
import sys
from typing import Iterable

from pie.utils import logger, add_log_argument, setup_file_logger, write_yaml
from pie import build_index


def parse_args(argv: Iterable[str] | None = None) -> argparse.Namespace:
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        description="Generate missing metadata fields for a YAML file",
    )
    parser.add_argument("input", help="Source YAML file")
    parser.add_argument("output", help="Destination file to write")
    add_log_argument(parser)
    return parser.parse_args(list(argv) if argv is not None else None)


def main(argv: Iterable[str] | None = None) -> None:
    """Entry point used by the ``process-yaml`` console script."""
    args = parse_args(argv)
    setup_file_logger(args.log)

    try:
        metadata = build_index.parse_yaml_metadata(args.input)
    except Exception as exc:  # pragma: no cover - pass through message
        logger.error("Failed to process YAML", filename=args.input)
        raise SystemExit(1) from exc

    if metadata is None:
        logger.error("No metadata found", filename=args.input)
        sys.exit(1)

    write_yaml(metadata, args.output)

    logger.info("Processed YAML written", path=args.output)


if __name__ == "__main__":
    main()
