from __future__ import annotations

from pathlib import Path

from ruamel.yaml import YAML

from pie.create import indextree
from pie.schema import DEFAULT_SCHEMA
from pie.utils import get_pubdate


yaml = YAML(typ="safe")


def test_indextree_create_generates_files(tmp_path: Path, monkeypatch) -> None:
    monkeypatch.chdir(tmp_path)
    target = Path("src") / "guides"

    exit_code = indextree.main([str(target)])

    assert exit_code == 0

    md_path = target / "index.md"
    yml_path = target / "index.yml"

    assert md_path.exists()
    assert yml_path.exists()

    expected_md = (
        "Explore this section through the tree below.\n\n"
        '<div class="indextree-root" data-src="/static/index/guides.json"></div>\n'
    )
    assert md_path.read_text(encoding="utf-8") == expected_md

    data = yaml.load(yml_path.read_text(encoding="utf-8"))

    assert data["press"]["id"] == "guides"
    assert data["schema"] == DEFAULT_SCHEMA
    assert data["url"] == "/guides/"
    assert data["html"] == {
        "scripts": [indextree.SCRIPT_TAG],
    }
    assert data["indextree"] == {"link": True}

    doc = data["doc"]
    assert doc["title"] == "Guides"
    assert doc["author"] == ""
    assert doc["pubdate"] == get_pubdate()
    assert doc["breadcrumbs"] == [
        {"title": "Home", "url": "/"},
        {"title": "Guides"},
    ]

    assert "description" not in data


def test_indextree_create_handles_nested_paths(tmp_path: Path, monkeypatch) -> None:
    monkeypatch.chdir(tmp_path)
    target = Path("src") / "docs" / "api"

    indextree.main([str(target)])

    md_path = target / "index.md"
    yml_path = target / "index.yml"

    expected_md = (
        "Explore this section through the tree below.\n\n"
        '<div class="indextree-root" data-src="/static/index/docs/api.json"></div>\n'
    )
    assert md_path.read_text(encoding="utf-8") == expected_md

    data = yaml.load(yml_path.read_text(encoding="utf-8"))

    assert data["press"]["id"] == "docs-api"
    assert data["url"] == "/docs/api/"
    assert data["doc"]["breadcrumbs"] == [
        {"title": "Home", "url": "/"},
        {"title": "Docs", "url": "/docs/"},
        {"title": "Api"},
    ]


def test_indextree_create_respects_overrides(tmp_path: Path, monkeypatch) -> None:
    monkeypatch.chdir(tmp_path)
    target = Path("src") / "reference"

    indextree.main(
        [
            str(target),
            "--title",
            "Reference",
            "--description",
            "API reference section",
            "--data-src",
            "/static/index/custom.json",
            "--url",
            "/docs/reference/",
            "--id",
            "custom-id",
        ]
    )

    md_path = target / "index.md"
    yml_path = target / "index.yml"

    assert md_path.read_text(encoding="utf-8") == (
        "Explore this section through the tree below.\n\n"
        '<div class="indextree-root" data-src="/static/index/custom.json"></div>\n'
    )

    data = yaml.load(yml_path.read_text(encoding="utf-8"))

    assert data["press"]["id"] == "custom-id"
    assert data["description"] == "API reference section"
    assert data["url"] == "/docs/reference/"
    assert data["doc"]["title"] == "Reference"
    assert data["doc"]["breadcrumbs"][-1] == {"title": "Reference"}
