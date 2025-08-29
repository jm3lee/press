"""Fill missing metadata fields in a YAML file after rendering Jinja."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path
from typing import Iterable

import copy

from ruamel.yaml import YAMLError
from jinja2 import TemplateSyntaxError

from pie.cli import create_parser
from pie.filter.emojify import emojify_text
from pie.logging import logger, configure_logging
from pie.render import jinja as render_jinja
from pie.utils import write_yaml
from pie.yaml import yaml
from pie.metadata import generate_missing_metadata


def parse_args(argv: Iterable[str] | None = None) -> argparse.Namespace:
    """Parse command line arguments."""
    parser = create_parser("Generate missing metadata fields for YAML files")
    parser.add_argument(
        "paths",
        nargs="+",
        help="YAML files to update in place",
    )
    return parser.parse_args(list(argv) if argv is not None else None)


def _emojify(value):
    """Recursively replace ``:emoji:`` codes in ``value``."""
    if isinstance(value, dict):
        return {k: _emojify(v) for k, v in value.items()}
    if isinstance(value, list):
        return [_emojify(v) for v in value]
    if isinstance(value, str):
        return emojify_text(value)
    return value


def _render_templates(value):
    """Recursively expand Jinja templates in ``value``."""
    if isinstance(value, dict):
        for k, v in value.items():
            value[k] = _render_templates(v)
        return value
    if isinstance(value, list):
        for i, v in enumerate(value):
            value[i] = _render_templates(v)
        return value
    if isinstance(value, str):
        rendered = render_jinja.render_jinja(value)
        if rendered == value:
            return value
        try:
            parsed = yaml.load(rendered)
        except YAMLError:
            parsed = rendered
        return _render_templates(parsed)
    return value


def _raise_processing_error(path: Path, exc: Exception) -> None:
    """Log ``exc`` and re-raise as ``SystemExit``."""
    kwargs = {"filename": str(path)}
    if isinstance(exc, TemplateSyntaxError):
        lineno = getattr(exc, "lineno", None)
        macro = getattr(exc, "name", None)
        source = getattr(exc, "source", None)
        if lineno is not None:
            kwargs["line"] = lineno
        if macro:
            kwargs["macro"] = macro
        if source:
            kwargs["template"] = source
    elif isinstance(exc, YAMLError):
        line = getattr(getattr(exc, "problem_mark", None), "line", None)
        if line is None:
            line = getattr(getattr(exc, "context_mark", None), "line", None)
        if line is not None:
            kwargs["line"] = line + 1
    logger.error("Failed to process YAML", **kwargs)
    raise SystemExit(1) from exc


def _process_path(path: Path) -> tuple[dict | None, dict | None, str | None, str | None]:
    """Return metadata and intermediate values for ``path``."""
    if path.exists():
        text = path.read_text(encoding="utf-8")
        rendered = render_jinja.render_jinja(text)
        existing = yaml.load(rendered)
        metadata = copy.deepcopy(existing) if existing is not None else None
    else:
        existing = None
        text = rendered = None
        metadata = {}
    if metadata is not None:
        render_jinja.index_json = metadata
        metadata = _render_templates(metadata)
        metadata = generate_missing_metadata(metadata, str(path))
        metadata = _render_templates(metadata)
        metadata = _emojify(metadata)
    return metadata, existing, rendered, text


def _unchanged(
    existing: dict | None,
    metadata: dict | None,
    rendered: str | None,
    text: str | None,
) -> bool:
    """Return ``True`` if no meaningful change was made."""
    return (
        existing is not None
        and existing == metadata
        and rendered is not None
        and text is not None
        and rendered.rstrip() == text.rstrip()
    )


def main(argv: Iterable[str] | None = None) -> None:
    """Entry point used by the ``process-yaml`` console script."""
    args = parse_args(argv)
    configure_logging(args.verbose, args.log)
    # ``render_jinja`` expects a mapping; default to an empty one.
    render_jinja.index_json = {}

    for path_str in args.paths:
        path = Path(path_str)
        try:
            metadata, existing, rendered, text = _process_path(path)
        except Exception as exc:  # pragma: no cover - pass through message
            _raise_processing_error(path, exc)

        if metadata is None:
            logger.error("No metadata found", filename=str(path))
            sys.exit(1)

        if _unchanged(existing, metadata, rendered, text):
            logger.debug("Processed YAML unchanged", path=str(path))
            continue

        write_yaml(metadata, str(path))
        logger.debug("Processed YAML written", path=str(path))


if __name__ == "__main__":
    main()
