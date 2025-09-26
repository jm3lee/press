import json
import os

import fakeredis
from pie import metadata, nginx_permalinks


def test_generates_redirects_from_redis(tmp_path, monkeypatch):
    src = tmp_path / "src"
    src.mkdir()
    (src / "doc.md").touch()

    fake = fakeredis.FakeRedis(decode_responses=True)
    monkeypatch.setattr(metadata, "redis_conn", fake)
    fake.set("src/doc.md", "doc")
    fake.set("doc.press.id", "doc")
    fake.set("doc.url", json.dumps("/doc.html"))
    fake.set("doc.permalink", json.dumps("/old.html"))

    out = tmp_path / "permalinks.conf"
    cwd = os.getcwd()
    os.chdir(tmp_path)
    try:
        nginx_permalinks.main(["src", "-o", str(out), "-v"])
    finally:
        os.chdir(cwd)

    assert out.read_text() == "location = /old.html {\n    return 301 /doc.html;\n}\n"


def test_load_metadata_adds_missing_id(monkeypatch):
    monkeypatch.setattr(
        nginx_permalinks,
        "get_metadata_by_path",
        lambda fp, key: "doc" if key == "press.id" else None,
    )
    monkeypatch.setattr(
        nginx_permalinks,
        "build_from_redis",
        lambda prefix: {"url": "/doc.html"},
    )

    meta = nginx_permalinks._load_metadata("doc.md")
    assert meta == {"url": "/doc.html", "press": {"id": "doc"}}


def test_load_metadata_handles_exceptions(monkeypatch):
    def bad_get(path, key):
        raise RuntimeError("boom")

    def bad_load(path):
        raise RuntimeError("boom")

    monkeypatch.setattr(nginx_permalinks, "get_metadata_by_path", bad_get)
    monkeypatch.setattr(nginx_permalinks, "load_metadata_pair", bad_load)

    assert nginx_permalinks._load_metadata("doc.md") is None


def test_collect_redirects_branches(tmp_path, monkeypatch):
    src = tmp_path / "src"
    src.mkdir()
    (src / "ignore.txt").touch()
    (src / "doc.md").touch()
    (src / "missing.md").touch()

    def fake_load(path):
        if path.endswith("doc.md"):
            return {"permalink": ["old", "older"], "url": "doc.html"}
        return None

    monkeypatch.setattr(nginx_permalinks, "_load_metadata", fake_load)
    redirects = nginx_permalinks.collect_redirects(str(src))
    assert redirects == [("old", "doc.html"), ("older", "doc.html")]


def test_main_prints_redirects(tmp_path, capsys, monkeypatch):
    src = tmp_path / "src"
    src.mkdir()

    monkeypatch.setattr(
        nginx_permalinks, "collect_redirects", lambda p: [("old", "doc.html")]
    )
    monkeypatch.setattr(nginx_permalinks, "configure_logging", lambda *a, **k: None)

    cwd = os.getcwd()
    os.chdir(tmp_path)
    try:
        nginx_permalinks.main(["src"])
    finally:
        os.chdir(cwd)

    assert (
        capsys.readouterr().out
        == "location = /old {\n    return 301 /doc.html;\n}\n"
    )
def test_fallbacks_to_load_metadata_pair(tmp_path, monkeypatch):
    src = tmp_path / "src"
    src.mkdir()
    md = src / "doc.md"
    md.write_text("---\npermalink: /old.html\n---\n")

    fake = fakeredis.FakeRedis(decode_responses=True)
    monkeypatch.setattr(metadata, "redis_conn", fake)

    out = tmp_path / "permalinks.conf"
    cwd = os.getcwd()
    os.chdir(tmp_path)
    try:
        nginx_permalinks.main(["src", "-o", str(out), "-v"])
    finally:
        os.chdir(cwd)

    assert out.read_text() == "location = /old.html {\n    return 301 /doc.html;\n}\n"
