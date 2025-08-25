from __future__ import annotations

"""Utilities for generating an HTML report of build check errors."""

import html


def parse_errors(output: str) -> dict[str, list[str]]:
    """Return mapping of check names to error lines from *output*.

    Lines beginning with ``==>`` denote the start of a check section.
    Only lines containing ``" E "`` are recorded as errors.
    """

    errors: dict[str, list[str]] = {}
    current: str | None = None
    for line in output.splitlines():
        if line.startswith("==>"):
            current = line[3:].strip()
        elif " E " in line:
            key = current or "General"
            errors.setdefault(key, []).append(line.strip())
    return errors


def render_html(errors: dict[str, list[str]]) -> str:
    """Return a minimal standalone HTML report for *errors*."""

    parts = [
        "<!DOCTYPE html>",
        "<html>",
        "<head>",
        '<meta charset="utf-8" />',
        "<title>Check Error Report</title>",
        "<style>body{font-family:sans-serif}h2{margin-top:1em}</style>",
        "</head>",
        "<body>",
        "<h1>Check Error Report</h1>",
    ]
    for section, lines in errors.items():
        parts.append(f"<h2>{html.escape(section)}</h2>")
        parts.append("<ul>")
        for line in lines:
            parts.append(f"<li>{html.escape(line)}</li>")
        parts.append("</ul>")
    parts.append("</body></html>")
    return "\n".join(parts) + "\n"
