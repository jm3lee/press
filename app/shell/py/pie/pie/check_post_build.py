#!/usr/bin/env python3
"""Check for required build artifacts."""

from __future__ import annotations

import argparse
from pathlib import Path
from pie.utils import logger, add_log_argument, setup_file_logger, read_yaml

DEFAULT_LOG = "log/check-post-build.txt"
DEFAULT_CFG = "cfg/check-post-build.yml"


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    """Return parsed command line arguments."""

    parser = argparse.ArgumentParser(
        description="Verify that expected build artifacts exist.",
    )
    parser.add_argument(
        "directory",
        nargs="?",
        default="build",
        help="Root directory containing build artifacts",
    )
    parser.add_argument(
        "-c",
        "--config",
        default=DEFAULT_CFG,
        help="YAML file listing required paths",
    )
    add_log_argument(parser, default=DEFAULT_LOG)
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    """Return ``0`` if all required files exist, ``1`` otherwise."""

    args = parse_args(argv)
    Path(args.log).parent.mkdir(parents=True, exist_ok=True)
    setup_file_logger(args.log)

    required = read_yaml(args.config) or []

    base = Path(args.directory)
    missing = False
    for rel in required:
        target = base / rel
        if target.is_file():
            logger.info("Found artifact", path=str(target))
        else:
            logger.error("Missing artifact", path=str(target))
            missing = True
    return 1 if missing else 0


if __name__ == "__main__":
    raise SystemExit(main())
