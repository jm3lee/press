from __future__ import annotations

from pathlib import Path

import yaml

from pie.create import post
from pie.utils import get_pubdate


def test_create_post_creates_files(tmp_path: Path) -> None:
    target = tmp_path / "blog" / "my-post"
    post.main([str(target)])

    md_file = target.with_suffix(".md")
    yml_file = target.with_suffix(".yml")

    assert md_file.exists(), "Markdown file should be created"
    assert yml_file.exists(), "YAML file should be created"

    data = yaml.safe_load(yml_file.read_text(encoding="utf-8"))
    assert set(data) == {"author", "pubdate", "title", "name"}
    assert data["name"] == "my-post"
    assert data["pubdate"] == get_pubdate()
