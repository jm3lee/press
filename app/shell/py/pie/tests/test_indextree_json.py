import os
import json
from pathlib import Path

from pie import indextree_json


def write_yaml(path: Path, data: dict) -> None:
    path.write_text(json.dumps(data))


def test_process_dir_builds_tree(tmp_path):
    """YAML files -> hierarchical tree."""
    src = tmp_path / "src"
    alpha = src / "alpha"
    alpha.mkdir(parents=True)
    write_yaml(alpha / "index.yml", {"id": "alpha", "name": "Alpha", "title": "Alpha"})
    write_yaml(alpha / "beta.yml", {"id": "beta", "name": "Beta", "title": "Beta"})
    write_yaml(src / "gamma.yml", {"id": "gamma", "name": "Gamma", "title": "Gamma"})

    os.chdir(tmp_path)
    try:
        data = list(indextree_json.process_dir(Path("src")))
    finally:
        os.chdir("/tmp")

    assert data == [
        {
            "id": "alpha",
            "label": "Alpha",
            "children": [
                {"id": "beta", "label": "Beta", "url": "/alpha/beta.html"}
            ],
            "url": "/alpha/index.html",
        },
        {"id": "gamma", "label": "Gamma", "url": "/gamma.html"},
    ]


def test_process_dir_honours_show_and_link(tmp_path):
    """show:False hides nodes; link:False omits URL."""
    src = tmp_path / "src"
    alpha = src / "alpha"
    delta = src / "delta"
    alpha.mkdir(parents=True)
    delta.mkdir(parents=True)

    write_yaml(alpha / "index.yml", {"id": "alpha", "name": "Alpha", "title": "Alpha"})
    write_yaml(alpha / "beta.yml", {
        "id": "beta",
        "name": "Beta",
        "title": "Beta",
        "gen-markdown-index": {"link": False},
    })
    write_yaml(src / "gamma.yml", {
        "id": "gamma",
        "name": "Gamma",
        "title": "Gamma",
        "gen-markdown-index": {"show": False},
    })
    write_yaml(delta / "index.yml", {
        "id": "delta",
        "name": "Delta",
        "title": "Delta",
        "gen-markdown-index": {"show": False},
    })
    write_yaml(delta / "epsilon.yml", {"id": "epsilon", "name": "Epsilon", "title": "Epsilon"})

    os.chdir(tmp_path)
    try:
        data = list(indextree_json.process_dir(Path("src")))
    finally:
        os.chdir("/tmp")

    assert data == [
        {
            "id": "alpha",
            "label": "Alpha",
            "children": [{"id": "beta", "label": "Beta"}],
            "url": "/alpha/index.html",
        },
        {"id": "epsilon", "label": "Epsilon", "url": "/delta/epsilon.html"},
    ]
