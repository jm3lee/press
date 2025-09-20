from pathlib import Path

from pie.update import breadcrumbs as update_breadcrumbs
from pie.yaml import yaml


def _read_frontmatter(path: Path) -> dict:
    text = path.read_text(encoding="utf-8")
    parts = text.split("---\n")
    if len(parts) < 3:
        return {}
    return yaml.load(parts[1]) or {}


def test_adds_frontmatter_breadcrumbs(tmp_path: Path, monkeypatch) -> None:
    """Markdown files gain breadcrumbs derived from their path."""

    src = tmp_path / "src" / "guides"
    src.mkdir(parents=True)
    md = src / "intro.md"
    md.write_text("---\ntitle: Intro\n---\nbody\n", encoding="utf-8")

    monkeypatch.chdir(tmp_path)

    update_breadcrumbs.main(["src"])

    frontmatter = _read_frontmatter(md)
    breadcrumbs = frontmatter["doc"]["breadcrumbs"]
    assert breadcrumbs == [
        {"title": "Home", "url": "/"},
        {"title": "Guides", "url": "/guides/"},
        {"title": "Intro"},
    ]


def test_updates_yaml_breadcrumbs(tmp_path: Path, monkeypatch) -> None:
    """Existing breadcrumbs are expanded to match the file structure."""

    src = tmp_path / "src" / "examples"
    src.mkdir(parents=True)
    yml = src / "demo.yml"
    yml.write_text(
        "doc:\n  breadcrumbs:\n  - title: Home\n    url: /\n",
        encoding="utf-8",
    )

    monkeypatch.chdir(tmp_path)

    update_breadcrumbs.main(["src"])

    data = yaml.load(yml.read_text(encoding="utf-8"))
    breadcrumbs = data["doc"]["breadcrumbs"]
    assert breadcrumbs == [
        {"title": "Home", "url": "/"},
        {"title": "Examples", "url": "/examples/"},
        {"title": "Demo"},
    ]


def test_preserves_custom_titles(tmp_path: Path, monkeypatch) -> None:
    """Breadcrumb titles remain unchanged while URLs are corrected."""

    src = tmp_path / "src" / "examples"
    src.mkdir(parents=True)
    yml = src / "demo.yml"
    yml.write_text(
        "doc:\n"
        "  breadcrumbs:\n"
        "  - title: Home\n"
        "  - title: Custom Examples\n"
        "    url: /wrong/\n"
        "  - title: Demo Page\n"
        "    url: /wrong/demo/\n",
        encoding="utf-8",
    )

    monkeypatch.chdir(tmp_path)

    update_breadcrumbs.main(["src"])

    data = yaml.load(yml.read_text(encoding="utf-8"))
    breadcrumbs = data["doc"]["breadcrumbs"]
    assert breadcrumbs == [
        {"title": "Home", "url": "/"},
        {"title": "Custom Examples", "url": "/examples/"},
        {"title": "Demo Page"},
    ]
