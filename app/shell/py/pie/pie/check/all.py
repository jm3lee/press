from __future__ import annotations

import argparse
from typing import Callable, Iterable

from pie.check import (
    author,
    bad_mathjax,
    unescaped_dollar,
    page_title,
    post_build,
    unexpanded_jinja,
    underscores,
    canonical,
    sitemap_hostname,
)

CheckFunc = Callable[[bool], int]

CHECKS: Iterable[tuple[str, CheckFunc]] = (
    (
        "Check metadata authors",
        lambda warn: author.main(["src"] + (["-w"] if warn else [])),
    ),
    (
        "Check for bad MathJax",
        lambda warn: bad_mathjax.main(["src"] + (["-w"] if warn else [])),
    ),
    (
        "Check for unescaped dollar signs",
        lambda warn: unescaped_dollar.main(["src"] + (["-w"] if warn else [])),
    ),
    (
        "Check page titles",
        lambda warn: page_title.main(
            [
                "-x",
                "cfg/check-page-title-exclude.yml",
                "build",
            ]
            + (["-w"] if warn else [])
        ),
    ),
    (
        "Check post-build artifacts",
        lambda warn: post_build.main(["-c", "cfg/check-post-build.yml"] + (["-w"] if warn else [])),
    ),
    (
        "Check for unexpanded Jinja",
        lambda warn: unexpanded_jinja.main(["build"] + (["-w"] if warn else [])),
    ),
    (
        "Check for URL underscores",
        lambda warn: underscores.main(["build"] + (["-w"] if warn else [])),
    ),
    (
        "Check canonical links",
        lambda warn: canonical.main(["build"] + (["-w"] if warn else [])),
    ),
    (
        "Check sitemap",
        lambda warn: sitemap_hostname.main(((["-w"] if warn else []))),
    ),
)


def main(argv: list[str] | None = None) -> int:
    """Run all checkers sequentially.

    This combines the existing stand-alone scripts into a single entry point,
    avoiding repeated Python start-up costs during a build.
    """

    parser = argparse.ArgumentParser(description="Run all checkers")
    parser.add_argument(
        "-w",
        "--warn",
        action="store_true",
        help="Treat errors as warnings and exit with success",
    )
    args = parser.parse_args(argv)

    ok = True
    for message, func in CHECKS:
        print(f"==> {message}")
        if func(args.warn) != 0:
            ok = False
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
