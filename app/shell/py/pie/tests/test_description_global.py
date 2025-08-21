import fakeredis
from pie.render import jinja as render_template
from pie import metadata


def test_description_renders_snippet():
    render_template.index_json = {"name": "world"}
    desc = {"description": "Hello {{ name }}"}
    assert render_template.description(desc) == "Hello world"


def test_description_loads_from_redis(monkeypatch):
    fake = fakeredis.FakeRedis(decode_responses=True)
    fake.set("entry.description", "Hi {{ thing }}")
    monkeypatch.setattr(metadata, "redis_conn", fake)
    monkeypatch.setattr(render_template, "_metadata_cache", {})
    render_template.index_json = {"thing": "there"}
    assert render_template.description("entry") == "Hi there"
