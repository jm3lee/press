
from __future__ import annotations

import argparse
from pathlib import Path
from typing import Iterable

from pie.cli import create_parser
from pie.logging import logger, configure_logging
from pie.render import jinja as render_jinja
from pie import flatfile
from pie.utils import read_utf8, write_yaml

__all__ = ["parse_args", "main"]

def parse_args(argv: Iterable[str] | None = None) -> argparse.Namespace:
    """Return parsed CLI arguments."""

    parser = create_parser("Convert a flatfile to YAML")
    parser.add_argument("input", help="Path to the input flatfile")
    parser.add_argument("output", help="Path to write the YAML output")
    return parser.parse_args(list(argv) if argv is not None else None)

def _convert(src: Path, dst: Path) -> None:
    """Read *src* flatfile, render templates and write YAML to *dst*."""

    text = read_utf8(str(src))
    rendered = render_jinja.render_jinja(text)
    data = flatfile.loads(rendered.splitlines())
    write_yaml(data, dst)

def main(argv: Iterable[str] | None = None) -> None:
    """Entry point for ``flatfile-to-yml`` console script."""

    args = parse_args(argv)
    configure_logging(args.verbose, args.log)
    render_jinja.index_json = {}
    try:
        _convert(Path(args.input), Path(args.output))
    except Exception as exc:  # pragma: no cover - propagate message
        logger.error(
            "Failed to convert flatfile", input=str(args.input), output=str(args.output)
        )
        raise SystemExit(1) from exc

if __name__ == "__main__":
    main()
