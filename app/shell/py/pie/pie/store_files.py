from __future__ import annotations

import argparse
import shutil
import string
import secrets
from pathlib import Path
from typing import Iterable, Sequence

from jinja2 import Environment

from pie.cli import create_parser
from pie.logging import configure_logging, logger
from pie.utils import read_yaml, write_utf8

__all__ = ["main"]


DEFAULT_CONFIG = Path("cfg") / "store-files.yml"
ALPHABET = string.ascii_letters + string.digits

_TEMPLATE_DIR = Path(__file__).with_name("templates")
_ENV = Environment(keep_trailing_newline=True)
METADATA_TEMPLATE = _ENV.from_string(
    (_TEMPLATE_DIR / "metadata.yml.jinja").read_text(encoding="utf-8")
)


def generate_id(size: int = 8) -> str:
    """Return a random identifier of *size* characters."""
    return "".join(secrets.choice(ALPHABET) for _ in range(size))


def iter_files(path: Path) -> Iterable[Path]:
    """Yield files under *path* recursively."""
    if path.is_dir():
        yield from (p for p in path.rglob("*") if p.is_file())
    elif path.is_file():
        yield path


def parse_args(argv: Sequence[str] | None = None) -> argparse.Namespace:
    """Parse command line arguments."""
    parser = create_parser("Move files to s3/v2 and create metadata entries")
    parser.add_argument(
        "paths",
        nargs="+",
        help="Paths to files or directories to process",
    )
    parser.add_argument(
        "-n",
        dest="limit",
        type=int,
        help="Limit number of files processed",
    )
    parser.add_argument(
        "-c",
        "--config",
        help="Path to configuration file (default: cfg/store-files.yml)",
    )
    return parser.parse_args(list(argv) if argv is not None else None)


def process_file(
    src: Path, dest_dir: Path, meta_dir: Path, *, baseurl: str = ""
) -> str:
    """Move *src* to *dest_dir* and create metadata in *meta_dir*.

    Returns the generated file identifier.
    """

    file_id = generate_id()
    dest_dir.mkdir(parents=True, exist_ok=True)
    meta_dir.mkdir(parents=True, exist_ok=True)

    dest_path = dest_dir / file_id
    shutil.move(str(src), dest_path)

    rendered = METADATA_TEMPLATE.render(baseurl=baseurl, file_id=file_id)
    meta_path = meta_dir / f"{file_id}.yml"
    write_utf8(rendered, str(meta_path))

    logger.info(
        "processed file",
        src=str(src),
        dest=str(dest_path),
        meta=str(meta_path),
    )
    return file_id


def main(argv: Sequence[str] | None = None) -> int:
    """Entry point for the ``store-files`` console script."""
    args = parse_args(argv)
    configure_logging(args.verbose, args.log)

    config_path = Path(args.config) if args.config else DEFAULT_CONFIG
    config: dict = {}
    if config_path.exists():
        config = read_yaml(str(config_path)) or {}
    elif args.config:
        logger.error("Missing config file", path=str(config_path))
        return 1

    baseurl = config.get("baseurl", "")

    dest_dir = Path("s3") / "v2" / "files" / "0"
    meta_dir = Path("src") / "static" / "files"

    count = 0
    for base in (Path(p) for p in args.paths):
        for src in iter_files(base):
            process_file(src, dest_dir, meta_dir, baseurl=baseurl)
            count += 1
            if args.limit and count >= args.limit:
                break
        if args.limit and count >= args.limit:
            break
    logger.info("completed", processed=count)
    return 0


if __name__ == "__main__":  # pragma: no cover - manual execution
    raise SystemExit(main())
