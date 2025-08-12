"""Deprecated command for processing YAML metadata."""

from __future__ import annotations

from typing import Iterable

from pie.logging import logger


def main(argv: Iterable[str] | None = None) -> None:
    """Entry point used by the ``process-yaml`` console script.

    This command has been deprecated and no longer performs any action.
    """
    logger.warning("process-yaml is deprecated and no longer needed")
    raise SystemExit(
        "process-yaml is deprecated; YAML metadata is processed automatically."
    )


if __name__ == "__main__":
    main()
