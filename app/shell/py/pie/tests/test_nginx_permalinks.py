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
    fake.set("doc.id", "doc")
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
