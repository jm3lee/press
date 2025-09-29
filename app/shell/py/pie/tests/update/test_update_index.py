import hashlib
import json
import os
import runpy
import sys
import threading
import warnings
from types import SimpleNamespace

import fakeredis
import pytest
from pie import metadata
from pie.update import index as update_index


def test_main_inserts_keys(tmp_path, monkeypatch):
    """JSON index -> Redis keys like quickstart.title."""
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
    """Lists become indexed Redis keys."""
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
    """Directory of yml -> Redis entries for each."""
    src = tmp_path / "src"
    src.mkdir()
    (src / "a.yml").write_text('{"title": "Foo"}')
    (src / "b.yml").write_text('{"title": "Bar"}')

    fake = fakeredis.FakeRedis(decode_responses=True)
    monkeypatch.setattr(update_index.redis, "Redis", lambda *a, **kw: fake)

    os.chdir(tmp_path)
    try:
        update_index.main(["src"])
    finally:
        os.chdir("/tmp")

    assert fake.get("a.title") == "Foo"
    assert fake.get("a.url") == "/a.html"
    assert fake.get("b.title") == "Bar"
    assert fake.get("b.url") == "/b.html"


def test_main_directory_skips_non_v1_schema(tmp_path, monkeypatch):
    """Metadata using schemas other than v1 are ignored."""
    src = tmp_path / "src"
    src.mkdir()
    (src / "a.yml").write_text('schema: v1\ntitle: Foo\n')
    (src / "b.yml").write_text('schema: v2\ntitle: Bar\n')

    fake = fakeredis.FakeRedis(decode_responses=True)
    monkeypatch.setattr(update_index.redis, "Redis", lambda *a, **kw: fake)

    os.chdir(tmp_path)
    try:
        update_index.main(["src"])
    finally:
        os.chdir("/tmp")

    assert fake.get("a.title") == "Foo"
    assert fake.get("b.title") is None


def test_main_single_yaml_file(tmp_path, monkeypatch):
    """Single YAML file populates Redis."""
    src = tmp_path / "src"
    src.mkdir()
    yml = src / "item.yml"
    yml.write_text('{"title": "Foo"}')

    fake = fakeredis.FakeRedis(decode_responses=True)
    monkeypatch.setattr(update_index.redis, "Redis", lambda *a, **kw: fake)

    os.chdir(tmp_path)
    try:
        update_index.main(["src/item.yml"])
    finally:
        os.chdir("/tmp")

    assert fake.get("item.title") == "Foo"
    assert fake.get("item.url") == "/item.html"


def test_main_single_yaml_non_v1_schema_errors(tmp_path, monkeypatch):
    """Processing a single v2 schema file aborts with an error."""
    src = tmp_path / "src"
    src.mkdir()
    yml = src / "item.yml"
    yml.write_text('schema: v2\ntitle: Foo\n')

    fake = fakeredis.FakeRedis(decode_responses=True)
    monkeypatch.setattr(update_index.redis, "Redis", lambda *a, **kw: fake)

    os.chdir(tmp_path)
    try:
        with pytest.raises(SystemExit):
            update_index.main(["src/item.yml"])
    finally:
        os.chdir("/tmp")

    assert fake.keys() == []


def test_main_combines_md_and_yaml(tmp_path, monkeypatch):
    """Markdown + YAML -> merged metadata."""
    src = tmp_path / "src"
    src.mkdir()
    md = src / "doc.md"
    md.write_text('---\n{"title": "Md", "foo": "bar"}\n---\n')
    yml = src / "doc.yml"
    yml.write_text('{"id": "doc", "title": "Yaml", "baz": "qux"}')

    fake = fakeredis.FakeRedis(decode_responses=True)
    monkeypatch.setattr(update_index.redis, "Redis", lambda *a, **kw: fake)

    messages = []

    def fake_warning(msg, *args, **kwargs):
        messages.append(msg.format(*args))

    monkeypatch.setattr(metadata.logger, "warning", fake_warning)

    os.chdir(tmp_path)
    try:
        update_index.main(["src/doc.md"])
    finally:
        os.chdir("/tmp")

    assert messages

    assert fake.get("doc.foo") == "bar"
    assert fake.get("doc.baz") == "qux"
    assert fake.get("doc.title") == "Yaml"


def test_main_adds_path_id_mapping(tmp_path, monkeypatch):
    """Each source path maps back to the document id."""
    src = tmp_path / "src"
    src.mkdir()
    md = src / "doc.md"
    md.write_text('---\n{"title": "Md"}\n---\n')
    yml = src / "doc.yml"
    yml.write_text('{"title": "Yaml"}')

    fake = fakeredis.FakeRedis(decode_responses=True)
    monkeypatch.setattr(update_index.redis, "Redis", lambda *a, **kw: fake)

    os.chdir(tmp_path)
    try:
        update_index.main(["src/doc.md"])
    finally:
        os.chdir("/tmp")

    assert fake.get("src/doc.md") == "doc"
    assert fake.get("src/doc.yml") == "doc"


def test_main_missing_id_generates(tmp_path, monkeypatch):
    """Missing id -> generated from filename."""
    src = tmp_path / "src"
    src.mkdir()
    md = src / "doc.md"
    md.write_text('---\n{"title": "T"}\n---\n')

    fake = fakeredis.FakeRedis(decode_responses=True)
    monkeypatch.setattr(update_index.redis, "Redis", lambda *a, **kw: fake)

    os.chdir(tmp_path)
    try:
        update_index.main(["src/doc.md"])
    finally:
        os.chdir("/tmp")

    assert fake.get("doc.title") == "T"


def test_metadata_schema_reads_nested_press_section():
    """_metadata_schema finds schema nested under the press key."""

    metadata = {"press": {"schema": "v1"}}

    assert update_index._metadata_schema(metadata) == "v1"


def test_flatten_index_logs_missing_source(tmp_path, monkeypatch):
    """Missing source files log a warning without interrupting processing."""

    cwd = os.getcwd()
    os.chdir(tmp_path)
    try:
        missing_index = {"doc": {"path": ["missing.md"], "title": "T"}}
        warnings_logged = []

        def fake_warning(message, **kwargs):
            warnings_logged.append((message, kwargs))

        monkeypatch.setattr(update_index.logger, "warning", fake_warning)

        entries = list(update_index.flatten_index(missing_index))
    finally:
        os.chdir(cwd)

    assert ("doc.title", "T") in entries
    assert any(msg == "Source file missing" for msg, _ in warnings_logged)


def test_load_directory_index_skips_invalid_and_missing(tmp_path, monkeypatch):
    """Non-metadata files and empty metadata entries are ignored."""

    src = tmp_path / "src"
    src.mkdir()

    def fake_walk(path):
        yield (str(src), [], ["doc.yml", "doc.md", "ignore.txt", "skip.yml"])

    monkeypatch.setattr(update_index.os, "walk", fake_walk)

    def fake_loader(path):
        if path.name == "skip.yml":
            return {}
        return {"id": path.stem, "title": path.stem}

    monkeypatch.setattr(update_index, "load_metadata_pair", fake_loader)

    index, processed = update_index.load_directory_index(src)

    assert index == {"doc": {"id": "doc", "title": "doc"}}
    assert processed == 2


def test_load_index_from_path_errors_without_metadata(tmp_path, monkeypatch):
    """Single metadata file with no parsed data aborts the update."""

    meta = tmp_path / "doc.yml"
    meta.write_text("title: Test\n", encoding="utf-8")

    monkeypatch.setattr(update_index, "load_metadata_pair", lambda path: None)

    errors = []

    def fake_error(message, **kwargs):
        errors.append((message, kwargs))

    monkeypatch.setattr(update_index.logger, "error", fake_error)

    with pytest.raises(SystemExit):
        update_index.load_index_from_path(meta)

    assert any(msg == "No metadata found" for msg, _ in errors)


def test_load_index_from_path_requires_document_id(tmp_path, monkeypatch):
    """Missing document ids emit a warning and abort."""

    meta = tmp_path / "doc.yml"
    meta.write_text("title: Test\n", encoding="utf-8")

    monkeypatch.setattr(update_index, "load_metadata_pair", lambda path: {"title": "T"})

    with warnings.catch_warnings(record=True) as caught:
        warnings.simplefilter("always")
        with pytest.raises(SystemExit):
            update_index.load_index_from_path(meta)

    assert any("Missing 'id' field" in str(w.message) for w in caught)


def test_load_index_from_path_rejects_unknown_suffix(tmp_path, monkeypatch):
    """Unsupported file types raise a SystemExit with a logged error."""

    doc = tmp_path / "doc.txt"
    doc.write_text("irrelevant", encoding="utf-8")

    errors = []

    def fake_error(message, **kwargs):
        errors.append((message, kwargs))

    monkeypatch.setattr(update_index.logger, "error", fake_error)

    with pytest.raises(SystemExit):
        update_index.load_index_from_path(doc)

    assert any(msg == "Unsupported file type" for msg, _ in errors)


def test_main_entrypoint_executes_when_run_as_script(tmp_path, monkeypatch):
    """Running the module as a script triggers main() exactly once."""

    idx = tmp_path / "index.json"
    idx.write_text('{"doc": {"title": "T"}}', encoding="utf-8")

    fake_redis = fakeredis.FakeRedis(decode_responses=True)
    monkeypatch.setitem(sys.modules, "redis", SimpleNamespace(Redis=lambda *a, **kw: fake_redis))

    argv = sys.argv
    sys.argv = ["update-index", str(idx)]
    try:
        runpy.run_path(update_index.__file__, run_name="__main__")
    finally:
        sys.argv = argv

    assert fake_redis.get("doc.title") == "T"


def test_directory_processed_in_parallel(tmp_path, monkeypatch):
    """Concurrent processing still populates Redis."""
    src = tmp_path / "src"
    src.mkdir()
    (src / "a.yml").write_text('{"title": "A"}')
    (src / "b.yml").write_text('{"title": "B"}')

    fake = fakeredis.FakeRedis(decode_responses=True)
    monkeypatch.setattr(update_index.redis, "Redis", lambda *a, **kw: fake)

    barrier = threading.Barrier(2)

    def fake_loader(path):
        barrier.wait(timeout=1)
        base = path.with_suffix("")
        return {"id": base.name, "title": base.name}

    monkeypatch.setattr(update_index, "load_metadata_pair", fake_loader)

    os.chdir(tmp_path)
    try:
        update_index.main(["src"])
    finally:
        os.chdir("/tmp")

    assert fake.get("a.title") == "a"
    assert fake.get("b.title") == "b"


def test_logs_execution_time_and_count(tmp_path, monkeypatch):
    """Logging shows file count and elapsed time."""
    src = tmp_path / "src"
    src.mkdir()
    (src / "a.yml").write_text('{"title": "A"}')
    (src / "b.yml").write_text('{"title": "B"}')

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


def test_verbose_enables_debug_logging(tmp_path, monkeypatch):
    """--verbose sets the console log level to DEBUG."""
    idx = tmp_path / "index.json"
    idx.write_text('{"doc": {"title": "T"}}')

    fake = fakeredis.FakeRedis(decode_responses=True)
    monkeypatch.setattr(update_index.redis, "Redis", lambda *a, **kw: fake)

    levels = []
    original_add = update_index.logger.add

    def fake_add(*args, **kwargs):
        levels.append(kwargs.get("level"))
        return original_add(*args, **kwargs)

    monkeypatch.setattr(update_index.logger, "add", fake_add)

    update_index.main(["--verbose", str(idx)])

    assert "DEBUG" in levels

    # Restore default logging configuration
    update_index.logger.remove()
    from pie.logging import LOG_FORMAT

    update_index.logger.add(sys.stderr, format=LOG_FORMAT, level="INFO")
