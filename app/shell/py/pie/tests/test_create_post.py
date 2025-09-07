from __future__ import annotations

from pathlib import Path

from ruamel.yaml import YAML

yaml = YAML(typ="safe")

from pie.create import post
from pie.utils import get_pubdate
from pie.metadata import CURRENT_SCHEMA


def test_create_post_creates_files(tmp_path: Path, monkeypatch) -> None:
    monkeypatch.chdir(tmp_path)
    target = Path("blog") / "my-post"
    post.main([str(target)])

    md_file = (tmp_path / target).with_suffix(".md")
    yml_file = (tmp_path / target).with_suffix(".yml")

    assert md_file.exists(), "Markdown file should be created"
    assert yml_file.exists(), "YAML file should be created"

    data = yaml.load(yml_file.read_text(encoding="utf-8"))
    assert set(data) == {"schema", "author", "pubdate", "title", "breadcrumbs"}
    assert data["schema"] == CURRENT_SCHEMA
    assert data["pubdate"] == get_pubdate()
    assert data["breadcrumbs"] == [
        {"title": "Home", "url": "/"},
        {"title": "Blog", "url": "/blog/"},
        {"title": "My Post"},
    ]
