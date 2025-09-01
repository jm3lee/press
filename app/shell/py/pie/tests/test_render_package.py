import pie.render as render_pkg


def test_render_package_exports_jinja():
    assert "jinja" in render_pkg.__all__
    assert hasattr(render_pkg, "jinja")


def test_render_package_exports_html():
    assert "html" in render_pkg.__all__
    assert hasattr(render_pkg, "html")
