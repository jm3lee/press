"""Helpers for generating redirect rules from metadata."""

from __future__ import annotations

import os
from typing import Iterable, List, Tuple, Dict, Any

from pie.metadata import get_url

Redirect = Tuple[str, str]
Redirects = List[Redirect]


def record_redirect(filepath: str, metadata: Dict[str, Any], redirects: Redirects) -> None:
    """Append a redirect rule if metadata['url'] differs from the derived path."""
    derived = get_url(filepath)
    canonical = metadata.get("url")
    if derived and canonical and derived != canonical:
        redirects.append((derived, canonical))


def write_redirects(redirects: Iterable[Redirect], output_path: str = os.path.join("build", "redirects.conf")) -> None:
    """Write Nginx rewrite rules to ``output_path``."""
    redirects = list(redirects)
    if not redirects:
        return
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as redirect_file:
        for src, dest in redirects:
            redirect_file.write(f"rewrite ^{src}$ {dest} permanent;\n")
