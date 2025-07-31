import json
import fakeredis
from pie import build_index_2


def test_main_inserts_keys(tmp_path, monkeypatch):
    index_data = {
        "quickstart": {
            "title": "Quickstart",
            "url": "/quickstart.html",
            "meta": {
                "subtitle": "Intro",
                "author": {"name": "Alice"},
            },
        }
    }
    idx = tmp_path / "index.json"
    idx.write_text(json.dumps(index_data))

    fake = fakeredis.FakeRedis(decode_responses=True)
    monkeypatch.setattr(build_index_2.redis, "Redis", lambda *a, **kw: fake)

    build_index_2.main([str(idx)])

    assert fake.get("quickstart.title") == "Quickstart"
    assert fake.get("quickstart.url") == "/quickstart.html"
    assert fake.get("quickstart.meta.subtitle") == "Intro"
    assert fake.get("quickstart.meta.author.name") == "Alice"


def test_main_handles_arrays(tmp_path, monkeypatch):
    index_data = {
        "quickstart": {
            "tags": ["foo", "bar"],
            "authors": [
                {"name": "Alice"},
                {"name": "Bob"},
            ],
        }
    }
    idx = tmp_path / "index.json"
    idx.write_text(json.dumps(index_data))

    fake = fakeredis.FakeRedis(decode_responses=True)
    monkeypatch.setattr(build_index_2.redis, "Redis", lambda *a, **kw: fake)

    build_index_2.main([str(idx)])

    assert fake.get("quickstart.tags.0") == "foo"
    assert fake.get("quickstart.tags.1") == "bar"
    assert fake.get("quickstart.authors.0.name") == "Alice"
    assert fake.get("quickstart.authors.1.name") == "Bob"
