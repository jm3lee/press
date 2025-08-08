"""Render Jinja expressions inside a study JSON file.

The script expands Jinja templates in multiple-choice question JSON files using
metadata from ``index.json``. It mirrors the behaviour of the original minimal
implementation but exposes a small command‐line interface and typed helper
functions for easier reuse.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any, Iterable, List

from pie.logging import logger, add_log_argument, setup_file_logger
from pie.utils import read_json

from .render_jinja_template import create_env


def render_study(index: dict[str, Any], questions: Iterable[dict[str, Any]]) -> List[dict[str, Any]]:
    """Expand Jinja templates for each question.

    Parameters
    ----------
    index:
        Mapping containing variables available to the templates.
    questions:
        Sequence of question dictionaries as loaded from the source JSON.

    Returns
    -------
    list of dict
        The questions with all template expressions rendered.
    """

    env = create_env()
    rendered: List[dict[str, Any]] = []
    for question in questions:
        q_text = env.from_string(question["q"]).render(**index)
        choices = [env.from_string(c).render(**index) for c in question["c"]]
        answer_idx, explanation = question["a"]
        explanation = env.from_string(explanation).render(**index)
        rendered.append({"q": q_text, "c": choices, "a": [answer_idx, explanation]})
    return rendered


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    """Parse command line arguments."""

    parser = argparse.ArgumentParser(
        description="Render a study JSON file by expanding Jinja templates",
    )
    parser.add_argument("index", help="Path to the index JSON providing variables")
    parser.add_argument("study", help="Path to the source study JSON file")
    parser.add_argument(
        "-o",
        "--output",
        help="Optional file to write the rendered JSON (defaults to stdout)",
    )
    add_log_argument(parser)
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> None:
    """Entry point for the ``pie.render_study_json`` module."""

    args = parse_args(argv)
    setup_file_logger(args.log)

    index_json = read_json(args.index)
    study_json = read_json(args.study)
    rendered = render_study(index_json, study_json)

    output_json = json.dumps(rendered, ensure_ascii=False)

    if args.output:
        Path(args.output).write_text(output_json, encoding="utf-8")
    else:
        print(output_json)


if __name__ == "__main__":
    main()
