import os
from pathlib import Path

os.environ.setdefault(
    "PIE_DATA_DIR",
    str(Path(__file__).resolve().parents[5] / "src" / "templates"),
)

import pie.render as render_pkg


def test_render_package_exports_jinja():
    assert "jinja" in render_pkg.__all__
    assert hasattr(render_pkg, "jinja")


def test_render_package_exports_html():
    assert "html" in render_pkg.__all__
    assert hasattr(render_pkg, "html")


def test_render_package_exports_press():
    assert "press" in render_pkg.__all__
    assert hasattr(render_pkg, "press")
