from __future__ import annotations

import argparse
from pathlib import Path
from typing import Sequence

from pie.utils import logger, add_log_argument, setup_file_logger


__all__ = ["main"]


def parse_args(argv: Sequence[str] | None = None) -> argparse.Namespace:
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        description="Create scaffolding for a Press project",
    )
    parser.add_argument("path", help="Target directory for the project")
    add_log_argument(parser)
    return parser.parse_args(list(argv) if argv is not None else None)


def main(argv: Sequence[str] | None = None) -> int:
    """Entry point for the ``create`` console script."""
    args = parse_args(argv)
    setup_file_logger(args.log)

    root = Path(args.path)
    root.mkdir(parents=True, exist_ok=True)

    # Create required files and directories
    (root / "docker-compose.yml").touch()
    (root / "src").mkdir(exist_ok=True)

    readme = root / "README.md"
    if not readme.exists():
        readme.write_text(
            "# New Press Project\n\n"
            "## Building\n\n"
            "Run `docker-compose build` to build the project.\n",
            encoding="utf-8",
        )

    logger.info("Created project scaffolding", path=str(root))
    return 0


if __name__ == "__main__":  # pragma: no cover - manual execution
    raise SystemExit(main())
