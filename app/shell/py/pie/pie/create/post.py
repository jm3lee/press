from __future__ import annotations

import argparse
from pathlib import Path
from typing import Sequence

from pie.cli import create_parser
from pie.model import Breadcrumb, Doc, Metadata
from pie.logging import configure_logging, logger
from pie.utils import get_pubdate, write_yaml


__all__ = ["main"]


def _title_from_slug(slug: str) -> str:
    """Return a human readable title from *slug*."""
    return slug.replace("-", " ").replace("_", " ").title()


def _id_from_slug(slug: str) -> str:
    """Return an identifier from *slug* using underscores."""

    return slug.replace("-", "_")


def parse_args(argv: Sequence[str] | None = None) -> argparse.Namespace:
    """Parse command line arguments."""
    parser = create_parser("Create a new post with Markdown and YAML files")
    parser.add_argument("path", help="Base path for the new post without extension")
    return parser.parse_args(list(argv) if argv is not None else None)


def main(argv: Sequence[str] | None = None) -> int:
    """Entry point for the ``create-post`` console script."""
    args = parse_args(argv)
    configure_logging(args.verbose, args.log)

    base = Path(args.path)
    base.parent.mkdir(parents=True, exist_ok=True)

    md_path = base.with_suffix(".md")
    yml_path = base.with_suffix(".yml")

    md_path.touch()
    try:
        rel_parts = base.resolve().relative_to(Path("src").resolve()).parts
    except ValueError:
        rel_parts = base.parts
    breadcrumbs: list[Breadcrumb] = [Breadcrumb("Home", "/")]
    url_parts: list[str] = []
    for part in rel_parts[:-1]:
        url_parts.append(part)
        breadcrumbs.append(
            Breadcrumb(
                _title_from_slug(part),
                "/" + "/".join(url_parts) + "/",
            )
        )
    slug = rel_parts[-1]
    breadcrumbs.append(Breadcrumb(_title_from_slug(slug)))
    metadata = Metadata(
        id=_id_from_slug(slug),
        doc=Doc(author="", pubdate=get_pubdate(), title=""),
        breadcrumbs=breadcrumbs,
    )
    write_yaml(metadata.to_dict(), str(yml_path))
    
    logger.info("Created post", md=str(md_path), yml=str(yml_path))
    return 0


if __name__ == "__main__":  # pragma: no cover - manual execution
    raise SystemExit(main())
