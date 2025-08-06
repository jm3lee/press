import json
import os
import threading
import fakeredis
import pytest
from pie import update_index


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
    monkeypatch.setattr(update_index.redis, "Redis", lambda *a, **kw: fake)

    update_index.main([str(idx)])

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
    monkeypatch.setattr(update_index.redis, "Redis", lambda *a, **kw: fake)

    update_index.main([str(idx)])

    assert fake.get("quickstart.tags.0") == "foo"
    assert fake.get("quickstart.tags.1") == "bar"
    assert fake.get("quickstart.authors.0.name") == "Alice"
    assert fake.get("quickstart.authors.1.name") == "Bob"


def test_main_directory_processes_yamls(tmp_path, monkeypatch):
    src = tmp_path / "src"
    src.mkdir()
    (src / "a.yml").write_text('{"name": "Foo"}')
    (src / "b.yml").write_text('{"name": "Bar"}')

    fake = fakeredis.FakeRedis(decode_responses=True)
    monkeypatch.setattr(update_index.redis, "Redis", lambda *a, **kw: fake)

    os.chdir(tmp_path)
    try:
        update_index.main(["src"])
    finally:
        os.chdir("/tmp")

    assert fake.get("a.name") == "Foo"
    assert fake.get("a.url") == "/a.html"
    assert fake.get("b.name") == "Bar"
    assert fake.get("b.url") == "/b.html"


def test_main_single_yaml_file(tmp_path, monkeypatch):
    src = tmp_path / "src"
    src.mkdir()
    yml = src / "item.yml"
    yml.write_text('{"name": "Foo"}')

    fake = fakeredis.FakeRedis(decode_responses=True)
    monkeypatch.setattr(update_index.redis, "Redis", lambda *a, **kw: fake)

    os.chdir(tmp_path)
    try:
        update_index.main(["src/item.yml"])
    finally:
        os.chdir("/tmp")

    assert fake.get("item.name") == "Foo"
    assert fake.get("item.url") == "/item.html"


def test_main_combines_md_and_yaml(tmp_path, monkeypatch):
    src = tmp_path / "src"
    src.mkdir()
    md = src / "doc.md"
    md.write_text("---\n{\"title\": \"Md\", \"foo\": \"bar\"}\n---\n")
    yml = src / "doc.yml"
    yml.write_text('{"id": "doc", "title": "Yaml", "baz": "qux", "name": "D"}')

    fake = fakeredis.FakeRedis(decode_responses=True)
    monkeypatch.setattr(update_index.redis, "Redis", lambda *a, **kw: fake)

    os.chdir(tmp_path)
    try:
        with pytest.warns(UserWarning):
            update_index.main(["src/doc.md"])
    finally:
        os.chdir("/tmp")

    assert fake.get("doc.foo") == "bar"
    assert fake.get("doc.baz") == "qux"
    assert fake.get("doc.title") == "Yaml"


def test_directory_pair_processed_once(tmp_path, monkeypatch):
    src = tmp_path / "src"
    src.mkdir()
    (src / "doc.md").write_text("---\n{\"title\": \"Md\"}\n---\n")
    (src / "doc.yml").write_text('{"title": "Yaml", "name": "D"}')

    fake = fakeredis.FakeRedis(decode_responses=True)
    monkeypatch.setattr(update_index.redis, "Redis", lambda *a, **kw: fake)

    os.chdir(tmp_path)
    try:
        with pytest.warns(UserWarning) as w:
            update_index.main(["src"])
    finally:
        os.chdir("/tmp")

    assert len(w) == 1
    assert fake.get("doc.title") == "Yaml"


def test_main_missing_id_generates(tmp_path, monkeypatch):
    src = tmp_path / "src"
    src.mkdir()
    md = src / "doc.md"
    md.write_text("---\n{\"title\": \"T\"}\n---\n")

    fake = fakeredis.FakeRedis(decode_responses=True)
    monkeypatch.setattr(update_index.redis, "Redis", lambda *a, **kw: fake)

    os.chdir(tmp_path)
    try:
        update_index.main(["src/doc.md"])
    finally:
        os.chdir("/tmp")

    assert fake.get("doc.title") == "T"


def test_directory_processed_in_parallel(tmp_path, monkeypatch):
    src = tmp_path / "src"
    src.mkdir()
    (src / "a.yml").write_text('{"name": "A"}')
    (src / "b.yml").write_text('{"name": "B"}')

    fake = fakeredis.FakeRedis(decode_responses=True)
    monkeypatch.setattr(update_index.redis, "Redis", lambda *a, **kw: fake)

    barrier = threading.Barrier(2)

    def fake_loader(path):
        barrier.wait(timeout=1)
        base = path.with_suffix("")
        return {"id": base.name, "name": base.name}

    monkeypatch.setattr(update_index, "load_metadata_pair", fake_loader)

    os.chdir(tmp_path)
    try:
        update_index.main(["src"])
    finally:
        os.chdir("/tmp")

    assert fake.get("a.name") == "a"
    assert fake.get("b.name") == "b"


def test_logs_execution_time_and_count(tmp_path, monkeypatch):
    src = tmp_path / "src"
    src.mkdir()
    (src / "a.yml").write_text('{"name": "A"}')
    (src / "b.yml").write_text('{"name": "B"}')

    fake = fakeredis.FakeRedis(decode_responses=True)
    monkeypatch.setattr(update_index.redis, "Redis", lambda *a, **kw: fake)

    calls = []

    def fake_info(msg, **kwargs):
        calls.append((msg, kwargs))

    monkeypatch.setattr(update_index.logger, "info", fake_info)

    os.chdir(tmp_path)
    try:
        update_index.main(["src"])
    finally:
        os.chdir("/tmp")

    assert any(msg == "update complete" and kw.get("files") == 2 for msg, kw in calls)
    assert any("elapsed" in kw for msg, kw in calls if msg == "update complete")
