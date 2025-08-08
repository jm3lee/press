from __future__ import annotations

import argparse
from pathlib import Path
from typing import Sequence

import yaml

from pie.utils import add_file_logger, logger

__all__ = ["main"]


def parse_args(argv: Sequence[str] | None = None) -> argparse.Namespace:
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        description="Create a new post with Markdown and YAML files",
    )
    parser.add_argument("path", help="Base path for the new post without extension")
    parser.add_argument(
        "-l",
        "--log",
        help="Write logs to the specified file",
    )
    return parser.parse_args(list(argv) if argv is not None else None)


def main(argv: Sequence[str] | None = None) -> int:
    """Entry point for the ``create-post`` console script."""
    args = parse_args(argv)
    if args.log:
        add_file_logger(args.log, level="INFO")

    base = Path(args.path)
    base.parent.mkdir(parents=True, exist_ok=True)

    md_path = base.with_suffix(".md")
    yml_path = base.with_suffix(".yml")

    md_path.touch()
    metadata = {"author": "", "pubdate": "", "title": "", "name": base.name}
    with yml_path.open("w", encoding="utf-8") as yf:
        yaml.safe_dump(metadata, yf, sort_keys=False)

    logger.info("Created post", md=str(md_path), yml=str(yml_path))
    return 0


if __name__ == "__main__":  # pragma: no cover - manual execution
    raise SystemExit(main())
