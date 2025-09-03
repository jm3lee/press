from __future__ import annotations

import argparse
from pathlib import Path
from typing import Sequence

from jinja2 import Environment

from pie.cli import create_parser
from pie.logging import logger, configure_logging


__all__ = ["main"]


def parse_args(argv: Sequence[str] | None = None) -> argparse.Namespace:
    """Parse command line arguments."""
    parser = create_parser("Create scaffolding for a Press project")
    parser.add_argument("path", help="Target directory for the project")
    return parser.parse_args(list(argv) if argv is not None else None)


def main(argv: Sequence[str] | None = None) -> int:
    """Entry point for the ``create`` console script."""
    args = parse_args(argv)
    configure_logging(args.verbose, args.log)

    root = Path(args.path)
    root.mkdir(parents=True, exist_ok=True)

    template_dir = Path(__file__).with_name("templates")
    env = Environment(keep_trailing_newline=True)

    files = {
        "docker-compose.yml": "docker-compose.yml.jinja",
        "src/index.md": "index.md.jinja",
        "src/index.yml": "index.yml.jinja",
        "src/css/style.css": "style.css.jinja",
        # Base HTML template used by render-html
        "src/templates/template.html.jinja": "template.html.jinja",
        "src/dep.mk": "dep.mk.jinja",
        "src/robots.txt": "robots.txt.jinja",
        "README.md": "README.md.jinja",
        "app/shell/Dockerfile": "shell.Dockerfile.jinja",
        "redo.mk": "redo.mk.jinja",
    }

    for rel_path, template_name in files.items():
        target = root / rel_path
        target.parent.mkdir(parents=True, exist_ok=True)
        template_text = (template_dir / template_name).read_text(
            encoding="utf-8"
        )
        if rel_path.endswith(".jinja"):
            # Preserve Jinja templates without rendering
            content = template_text
        else:
            content = env.from_string(template_text).render()
        target.write_text(content, encoding="utf-8")

    logger.info("Created project scaffolding", path=str(root))
    return 0


if __name__ == "__main__":  # pragma: no cover - manual execution
    raise SystemExit(main())
