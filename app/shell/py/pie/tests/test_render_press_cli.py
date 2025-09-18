import os
from pathlib import Path

os.environ.setdefault(
    "PIE_DATA_DIR",
    "/data/src/templates",
)

from pie.render import press


def test_main_renders_markdown_file(tmp_path):
    markdown = tmp_path / "doc.md"
    markdown.write_text("Hello :smile:\n", encoding="utf-8")
    output = tmp_path / "doc.html"
    press.main([str(markdown), str(output)])
    html = output.read_text(encoding="utf-8")
    assert "Hello 😄" in html


def test_main_renders_footnotes(tmp_path):
    markdown = tmp_path / "doc.md"
    markdown.write_text("Note.[^1]\n\n[^1]: Footnote", encoding="utf-8")
    output = tmp_path / "doc.html"
    press.main([str(markdown), str(output)])
    html = output.read_text(encoding="utf-8")
    assert '<section class="footnotes"' in html
