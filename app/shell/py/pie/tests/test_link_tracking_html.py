"""Tests related to HTML output when link tracking is disabled."""

import re
from pathlib import Path

import pytest
import yaml

from pie import render_template


def _collect_tracking_disabled_urls(src_root: Path) -> list[str]:
    """Return URLs from ``*.yml`` files with ``link.tracking: false``."""
    urls: list[str] = []
    for yml in src_root.rglob("*.yml"):
        data = yaml.safe_load(yml.read_text(encoding="utf-8"))
        if isinstance(data, dict):
            link = data.get("link", {})
            if isinstance(link, dict) and link.get("tracking") is False:
                url = data.get("url")
                if url:
                    urls.append(url)
    return urls


def test_tracking_false_links_have_attributes():
    """Ensure disabled-tracking links in HTML have the expected attributes."""

    build_dir = Path("build")
    if not build_dir.is_dir():
        pytest.skip("build directory not found")

    # All rendered HTML files under build/
    html_files = list(build_dir.rglob("*.html"))
    if not html_files:
        pytest.skip("no html files found in build")

    # Collect every link marked with tracking: false from src/
    urls = _collect_tracking_disabled_urls(Path("src"))
    if not urls:
        pytest.skip("no links with tracking=false found")

    expected_attrs = render_template.get_tracking_options({"link": {"tracking": False}})

    for url in urls:
        # Look for anchor tags with this href across all HTML files
        pattern = rf'<a[^>]*href="{re.escape(url)}"[^>]*>'
        found = False
        for html_path in html_files:
            html = html_path.read_text(encoding="utf-8")
            anchors = re.findall(pattern, html)
            if anchors:
                found = True
                # Every occurrence should contain the expected attributes
                for tag in anchors:
                    assert expected_attrs in tag
        assert found, f"Link to {url} not found"
