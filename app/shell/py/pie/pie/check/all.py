from __future__ import annotations

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

CheckFunc = Callable[[], int]

CHECKS: Iterable[tuple[str, CheckFunc]] = (
    ("Check metadata authors", lambda: author.main(["src"])),
    ("Check for bad MathJax", lambda: bad_mathjax.main(["src"])),
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


def main(argv: list[str] | None = None) -> int:
    """Run all checkers sequentially.

    This combines the existing stand-alone scripts into a single entry
    point, avoiding repeated Python start-up costs during a build.
    """

    ok = True
    for message, func in CHECKS:
        print(f"==> {message}")
        if func() != 0:
            ok = False
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
