import subprocess
from pathlib import Path

from bs4 import BeautifulSoup
import pytest


def run_pandoc(tmp_path: Path, permalink: str | None) -> str:
    """Render minimal markdown with optional permalink and return HTML."""
    lines = ["---", "title: Sample"]
    if permalink:
        lines.append(f"permalink: {permalink}")
    lines.append("---\n\nBody")
    md_path = tmp_path / "doc.md"
    md_path.write_text("\n".join(lines), encoding="utf-8")

    html_path = tmp_path / "out.html"
    template = Path(__file__).resolve().parents[5] / "src" / "pandoc-template.html"
    cmd = [
        "pandoc",
        "--standalone",
        "--template",
        str(template),
        str(md_path),
        "-o",
        str(html_path),
    ]
    subprocess.run(cmd, check=True)
    return html_path.read_text(encoding="utf-8")


@pytest.mark.parametrize("url", ["https://example.com/a", "/relative/path"])
def test_permalink_sets_canonical(tmp_path: Path, url: str) -> None:
    html = run_pandoc(tmp_path, url)
    soup = BeautifulSoup(html, "html.parser")
    link = soup.find("link", rel="canonical")
    assert link is not None
    assert link.get("href") == url


def test_no_permalink_has_no_canonical(tmp_path: Path) -> None:
    html = run_pandoc(tmp_path, None)
    soup = BeautifulSoup(html, "html.parser")
    assert soup.find("link", rel="canonical") is None

