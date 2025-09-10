from __future__ import annotations

import argparse
from pathlib import Path
from typing import Iterable, Sequence

from bs4 import BeautifulSoup

from pie.cli import create_parser
from pie.logging import configure_logging, logger

__all__ = ["main"]


def parse_args(argv: Sequence[str] | None = None) -> argparse.Namespace:
    """Return parsed command line arguments."""
    parser = create_parser("Generate report of static links")
    parser.add_argument(
        "build_dir",
        nargs="?",
        default="build",
        help="Directory containing HTML files (default: build)",
    )
    parser.add_argument(
        "-o",
        "--output",
        default="report/static-links.html",
        help="Path to output report (default: report/static-links.html)",
    )
    return parser.parse_args(list(argv) if argv is not None else None)


def iter_html_files(path: Path) -> Iterable[Path]:
    """Yield HTML files under *path* recursively."""
    yield from path.rglob("*.html")


def extract_links(path: Path) -> list[str]:
    """Return sorted list of links from *path*."""
    soup = BeautifulSoup(path.read_text(encoding="utf-8"), "html.parser")
    urls = {a["href"] for a in soup.find_all("a", href=True)}
    return sorted(urls)


def generate_report(links: dict[Path, list[str]], dest: Path) -> None:
    """Write *links* report to *dest* as HTML."""
    dest.parent.mkdir(parents=True, exist_ok=True)
    with dest.open("w", encoding="utf-8") as fh:
        fh.write("<html><body>\n")
        for path, urls in links.items():
            fh.write(f"<h2>{path}</h2>\n<ul>\n")
            for url in urls:
                fh.write(f"  <li>{url}</li>\n")
            fh.write("</ul>\n")
        fh.write("</body></html>\n")


def main(argv: Sequence[str] | None = None) -> int:
    """Entry point for ``report-static-links``."""
    args = parse_args(argv)
    configure_logging(args.verbose, args.log)

    build_dir = Path(args.build_dir)
    report_path = Path(args.output)

    links: dict[Path, list[str]] = {}
    for html_file in iter_html_files(build_dir):
        rel = html_file.relative_to(build_dir)
        links[rel] = extract_links(html_file)
    links = dict(sorted(links.items()))

    generate_report(links, report_path)
    logger.info("wrote report", path=str(report_path))
    return 0


if __name__ == "__main__":  # pragma: no cover - manual execution
    raise SystemExit(main())
