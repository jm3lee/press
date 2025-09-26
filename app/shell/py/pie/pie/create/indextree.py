from __future__ import annotations

"""Create Markdown and metadata scaffolding for an IndexTree section."""

import argparse
from pathlib import Path
from typing import Sequence

from pie.cli import create_parser
from pie.logging import configure_logging, logger
from pie.model import Breadcrumb, Doc, Metadata, Press, PubDate
from pie.utils import write_yaml

SCRIPT_TAG = '<script type="module" src="/static/js/indextree.js" defer></script>'
DEFAULT_MD_TEMPLATE = (
    "Explore this section through the tree below.\n\n"
    '<div class="indextree-root" data-src="{data_src}"></div>\n'
)

__all__ = ["main"]


def _title_from_slug(slug: str) -> str:
    """Return a title-cased string derived from *slug*."""

    return slug.replace("-", " ").replace("_", " ").title()


def _relative_parts(directory: Path) -> list[str]:
    """Return path components relative to ``src/`` when available."""

    src_root = Path("src").resolve()
    try:
        rel = directory.resolve().relative_to(src_root)
        parts = [part for part in rel.parts if part not in {"", "."}]
        if parts:
            return parts
    except ValueError:
        pass
    return [directory.resolve().name]


def _build_breadcrumbs(parts: list[str], final_title: str) -> list[Breadcrumb]:
    """Return breadcrumbs for *parts* including the implicit Home link."""

    breadcrumbs: list[Breadcrumb] = [Breadcrumb("Home", "/")]
    url_parts: list[str] = []
    for index, part in enumerate(parts):
        title = final_title if index == len(parts) - 1 else _title_from_slug(part)
        url_parts.append(part)
        if index == len(parts) - 1:
            breadcrumbs.append(Breadcrumb(title))
        else:
            url = "/" + "/".join(url_parts) + "/"
            breadcrumbs.append(Breadcrumb(title, url))
    return breadcrumbs


def _build_doc_id(parts: list[str]) -> str:
    """Return a document identifier based on *parts*."""

    return "-".join(part.replace("_", "-").lower() for part in parts)


def _build_data_src(parts: list[str]) -> str:
    """Return the ``data-src`` attribute for the generated Markdown."""

    rel_path = "/".join(parts)
    return f"/static/index/{rel_path}.json"


def _build_metadata(
    doc_id: str,
    title: str,
    breadcrumbs: list[Breadcrumb],
    url: str,
    description: str | None = None,
) -> dict[str, object]:
    """Return metadata dictionary for the IndexTree page."""

    metadata = Metadata(
        press=Press(id=doc_id),
        doc=Doc(
            author="",
            pubdate=PubDate(),
            title=title,
            breadcrumbs=breadcrumbs,
        ),
        description=description,
    ).to_dict()
    metadata["html"] = {"scripts": [SCRIPT_TAG]}
    metadata["indextree"] = {"link": True}
    metadata["url"] = url
    return metadata


def parse_args(argv: Sequence[str] | None = None) -> argparse.Namespace:
    """Parse command line arguments."""

    parser = create_parser("Create metadata for an IndexTree directory")
    parser.add_argument(
        "path",
        help="Directory that should contain index.md and index.yml",
    )
    parser.add_argument(
        "--title",
        help="Override the generated title for the index page",
    )
    parser.add_argument(
        "--description",
        help="Optional description stored in index.yml",
    )
    parser.add_argument(
        "--data-src",
        help="Custom data-src value for the generated Markdown",
    )
    parser.add_argument(
        "--url",
        help="Explicit URL to store in index.yml (defaults to derived path)",
    )
    parser.add_argument(
        "--id",
        help="Explicit document identifier (defaults to derived value)",
    )
    return parser.parse_args(list(argv) if argv is not None else None)


def main(argv: Sequence[str] | None = None) -> int:
    """Entry point for the ``indextree-create`` console script."""

    args = parse_args(argv)
    configure_logging(args.verbose, args.log)

    directory = Path(args.path)
    directory.mkdir(parents=True, exist_ok=True)

    parts = _relative_parts(directory)
    title = args.title or _title_from_slug(parts[-1])
    doc_id = args.id or _build_doc_id(parts)
    data_src = args.data_src or _build_data_src(parts)
    url = args.url or "/" + "/".join(parts) + "/"

    md_path = directory / "index.md"
    md_path.write_text(DEFAULT_MD_TEMPLATE.format(data_src=data_src), encoding="utf-8")

    metadata = _build_metadata(
        doc_id=doc_id,
        title=title,
        breadcrumbs=_build_breadcrumbs(parts, title),
        url=url,
        description=args.description,
    )
    yml_path = directory / "index.yml"
    write_yaml(metadata, yml_path)

    logger.info(
        "Created IndexTree files",
        directory=str(directory),
        md=str(md_path),
        yml=str(yml_path),
    )
    return 0


if __name__ == "__main__":  # pragma: no cover - manual execution
    raise SystemExit(main())
