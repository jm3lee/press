import os
import json
import sys
from pathlib import Path

import fakeredis
import pytest
from pie.logging import logger
import io

from pie import indextree_json, metadata


def save_meta(store: fakeredis.FakeRedis, filepath: str, doc_id: str, meta: dict) -> None:
    """Store *meta* for *doc_id* and map *filepath* to that id."""
    store.set(filepath, doc_id)

    meta_with_id = {"id": doc_id, **meta}

    def recurse(prefix: str, data: dict) -> None:
        for key, value in data.items():
            if isinstance(value, dict):
                recurse(f"{prefix}{key}.", value)
            else:
                if key == "id":
                    store.set(prefix + key, value)
                else:
                    store.set(prefix + key, json.dumps(value))

    recurse(f"{doc_id}.", meta_with_id)


def test_process_dir_builds_tree(tmp_path, monkeypatch):
    """Redis metadata -> hierarchical tree."""
    src = tmp_path / "src"
    alpha = src / "alpha"
    alpha.mkdir(parents=True)
    (alpha / "index.yml").touch()
    (alpha / "beta.yml").touch()
    (src / "gamma.yml").touch()

    fake = fakeredis.FakeRedis(decode_responses=True)
    monkeypatch.setattr(metadata, "redis_conn", fake)

    save_meta(fake, "src/alpha/index.yml", "alpha", {"title": "Alpha", "url": "/alpha/index.html"})
    save_meta(fake, "src/alpha/beta.yml", "beta", {"title": "Beta", "url": "/alpha/beta.html"})
    save_meta(fake, "src/gamma.yml", "gamma", {"title": "Gamma", "url": "/gamma.html"})

    os.chdir(tmp_path)
    try:
        data = list(indextree_json.process_dir(Path("src")))
    finally:
        os.chdir("/tmp")

    assert data == [
        {
            "id": "a",
            "label": "Alpha",
            "children": [
                {"id": "b", "label": "Beta", "url": "/alpha/beta.html"}
            ],
            "url": "/alpha/index.html",
        },
        {"id": "g", "label": "Gamma", "url": "/gamma.html"},
    ]


def test_process_dir_honours_show_and_link(tmp_path, monkeypatch):
    """show:False hides nodes; link:False omits URL."""
    src = tmp_path / "src"
    alpha = src / "alpha"
    delta = src / "delta"
    alpha.mkdir(parents=True)
    delta.mkdir(parents=True)

    (alpha / "index.yml").touch()
    (alpha / "beta.yml").touch()
    (src / "gamma.yml").touch()
    (delta / "index.yml").touch()
    (delta / "epsilon.yml").touch()

    fake = fakeredis.FakeRedis(decode_responses=True)
    monkeypatch.setattr(metadata, "redis_conn", fake)

    save_meta(fake, "src/alpha/index.yml", "alpha", {"title": "Alpha", "url": "/alpha/index.html"})
    save_meta(
        fake,
        "src/alpha/beta.yml",
        "beta",
        {"title": "Beta", "url": "/alpha/beta.html", "indextree": {"link": False}},
    )
    save_meta(
        fake,
        "src/gamma.yml",
        "gamma",
        {"title": "Gamma", "url": "/gamma.html", "indextree": {"show": False}},
    )
    save_meta(
        fake,
        "src/delta/index.yml",
        "delta",
        {"title": "Delta", "url": "/delta/index.html", "indextree": {"show": False}},
    )
    save_meta(fake, "src/delta/epsilon.yml", "epsilon", {"title": "Epsilon", "url": "/delta/epsilon.html"})

    os.chdir(tmp_path)
    try:
        data = list(indextree_json.process_dir(Path("src")))
    finally:
        os.chdir("/tmp")

    assert data == [
        {
            "id": "a",
            "label": "Alpha",
            "children": [{"id": "b", "label": "Beta"}],
            "url": "/alpha/index.html",
        },
        {"id": "e", "label": "Epsilon", "url": "/delta/epsilon.html"},
    ]


def test_process_dir_generates_short_unique_ids(tmp_path, monkeypatch):
    """Identifiers are shortened to minimal unique prefixes and labels stay intact."""
    src = tmp_path / "src"
    src.mkdir()
    (src / "one.yml").touch()
    (src / "two.yml").touch()
    (src / "three.yml").touch()

    fake = fakeredis.FakeRedis(decode_responses=True)
    monkeypatch.setattr(metadata, "redis_conn", fake)

    ids = ["abcdef", "abcxyz", "abcpqr"]
    labels = [
        "First Node With An Extremely Long Label",
        "Second Node With An Extremely Long Label",
        "Third Node With An Extremely Long Label",
    ]
    for file, doc_id, label in zip(["one.yml", "two.yml", "three.yml"], ids, labels):
        save_meta(fake, f"src/{file}", doc_id, {"title": label})

    os.chdir(tmp_path)
    try:
        data = list(indextree_json.process_dir(Path("src")))
    finally:
        os.chdir("/tmp")

    assert data == [
        {"id": "abcd", "label": labels[0]},
        {"id": "abcx", "label": labels[1]},
        {"id": "abcp", "label": labels[2]},
    ]

    log_path = tmp_path / "short_ids.map.json"
    assert json.loads(log_path.read_text()) == {
        "abcdef": "abcd",
        "abcxyz": "abcx",
        "abcpqr": "abcp",
    }


def test_main_writes_output_file(tmp_path, monkeypatch, capsys):
    """JSON is written to file when an output path is provided."""
    src = tmp_path / "src"
    src.mkdir()
    (src / "alpha.yml").touch()

    fake = fakeredis.FakeRedis(decode_responses=True)
    monkeypatch.setattr(metadata, "redis_conn", fake)
    save_meta(fake, "src/alpha.yml", "alpha", {"title": "Alpha", "url": "/alpha.html"})

    output_path = tmp_path / "tree.json"

    os.chdir(tmp_path)
    monkeypatch.setattr(
        sys, "argv", ["indextree-json", "src", str(output_path)]
    )
    try:
        indextree_json.main()
    finally:
        os.chdir("/tmp")

    captured = capsys.readouterr()
    assert captured.out == ""
    assert json.loads(output_path.read_text()) == [
        {"id": "a", "label": "Alpha", "url": "/alpha.html"}
    ]
    assert json.loads(Path(f"{output_path}.map.json").read_text()) == {"alpha": "a"}


def test_main_reports_missing_title(tmp_path, monkeypatch):
    """Missing title logs an error and exits."""
    src = tmp_path / "src"
    src.mkdir()
    (src / "alpha.yml").touch()

    fake = fakeredis.FakeRedis(decode_responses=True)
    monkeypatch.setattr(metadata, "redis_conn", fake)
    save_meta(fake, "src/alpha.yml", "alpha", {"url": "/alpha.html"})

    log_output = io.StringIO()
    handler_id = logger.add(log_output, level="ERROR")

    os.chdir(tmp_path)
    monkeypatch.setattr(sys, "argv", ["indextree-json", "src"])
    try:
        with pytest.raises(SystemExit):
            indextree_json.main()
    finally:
        os.chdir("/tmp")
        logger.remove(handler_id)

    assert "Missing 'title' in src/alpha.yml" in log_output.getvalue()
