"""Tests related to HTML output when link tracking is disabled."""

import re
import traceback
import warnings
from pathlib import Path

from bs4 import BeautifulSoup

import pytest
import yaml
from pie.render import jinja as render_template


def _collect_tracking_disabled_urls(src_root: Path) -> list[str]:
    """Return URLs from ``*.yml`` files with ``link.tracking: false``."""
    urls: list[str] = []
    for yml in src_root.rglob("*.yml"):
        try:
            data = yaml.safe_load(yml.read_text(encoding="utf-8"))
            if isinstance(data, dict):
                link = data.get("link", {})
                if isinstance(link, dict) and link.get("tracking") is False:
                    url = data.get("url")
                    if url:
                        urls.append(url)
        except Exception as e:
            traceback.print_exc()
            warnings.warn(f"Can't load and parse {yml} due to {e}", UserWarning)
    return urls


def test_tracking_false_links_have_attributes():
    """Links with ``tracking: false`` -> rel/target attrs."""

    build_dir = Path("/data/build")
    if not build_dir.is_dir():
        pytest.skip(f"build directory, {build_dir}, not found")

    # All rendered HTML files under build/
    html_files = list(build_dir.rglob("*.html"))
    if not html_files:
        pytest.skip("no html files found in build")

    # Collect every link marked with tracking: false from src/
    urls = _collect_tracking_disabled_urls(Path("/data/src"))
    if not urls:
        pytest.skip("no links with tracking=false found")

    expected_attrs = render_template.get_tracking_options({"link": {"tracking": False}})
    attrs = dict(re.findall(r'(\w+)="([^"]+)"', expected_attrs))
    expected_rel = attrs.get("rel")
    expected_target = attrs.get("target")

    for url in urls:
        found = False
        for html_path in html_files:
            with open(html_path, "r", encoding="utf-8") as f:
                soup = BeautifulSoup(f, "html.parser")
            anchors = soup.find_all("a", href=url)
            if anchors:
                found = True
                for tag in anchors:
                    if expected_rel:
                        rel_values = tag.get("rel", [])
                        if isinstance(rel_values, str):
                            rel_values = rel_values.split()
                        for value in expected_rel.split():
                            assert value in rel_values
                    if expected_target:
                        assert tag.get("target") == expected_target
        if not found:
            warnings.warn(f"Link to {url} not found", UserWarning)
