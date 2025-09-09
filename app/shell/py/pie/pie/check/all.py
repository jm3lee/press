from __future__ import annotations

import io
import sys
from contextlib import redirect_stderr, redirect_stdout
from pathlib import Path
from typing import Callable, Iterable

from pie.check import (
    author,
    unescaped_dollar,
    page_title,
    breadcrumbs,
    post_build,
    unexpanded_jinja,
    underscores,
    canonical,
    sitemap_hostname,
    report,
)

CheckFunc = Callable[[], int]

OUTPUT_PATH = Path("log/report.html")

CHECKS: Iterable[tuple[str, CheckFunc]] = (
    ("Check metadata authors", lambda: author.main(["src"])),
    (
        "Check for unescaped dollar signs",
        lambda: unescaped_dollar.main(["src"]),
    ),
    (
        "Check page titles",
        lambda: page_title.main([
            "-x",
            "cfg/check-page-title-exclude.yml",
            "build",
        ]),
    ),
    ("Check breadcrumbs", lambda: breadcrumbs.main(["src"])),
    (
        "Check post-build artifacts",
        lambda: post_build.main(["-c", "cfg/check-post-build.yml"]),
    ),
    (
        "Check for unexpanded Jinja",
        lambda: unexpanded_jinja.main(["build"]),
    ),
    (
        "Check for URL underscores",
        lambda: underscores.main(["build"]),
    ),
    ("Check canonical links", lambda: canonical.main(["build"])),
    ("Check sitemap", lambda: sitemap_hostname.main([])),
)


class _Tee(io.TextIOBase):
    def __init__(self, stream: io.TextIOBase, buffer: io.StringIO) -> None:
        self.stream = stream
        self.buffer = buffer

    def write(self, s: str) -> int:  # type: ignore[override]
        self.stream.write(s)
        self.buffer.write(s)
        return len(s)

    def flush(self) -> None:  # type: ignore[override]
        self.stream.flush()


def main(argv: list[str] | None = None) -> int:
    """Run all checkers sequentially and write an error report."""

    buffer = io.StringIO()
    tee_out = _Tee(sys.stdout, buffer)
    tee_err = _Tee(sys.stderr, buffer)

    with redirect_stdout(tee_out), redirect_stderr(tee_err):
        ok = True
        for message, func in CHECKS:
            print(f"==> {message}")
            if func() != 0:
                ok = False

    errors = report.parse_errors(buffer.getvalue())
    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT_PATH.write_text(report.render_html(errors), encoding="utf-8")
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
