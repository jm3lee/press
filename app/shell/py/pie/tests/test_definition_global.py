import fakeredis
from pie.render import jinja as render_template
from pie import metadata


def test_definition_renders_snippet():
    render_template.index_json = {"name": "world"}
    desc = {"definition": "Hello {{ name }}"}
    assert render_template.definition(desc) == "Hello world"


def test_definition_loads_from_redis(monkeypatch):
    fake = fakeredis.FakeRedis(decode_responses=True)
    fake.set("entry.definition", "Hi {{ thing }}")
    monkeypatch.setattr(metadata, "redis_conn", fake)
    monkeypatch.setattr(render_template, "_metadata_cache", {})
    render_template.index_json = {"thing": "there"}
    assert render_template.definition("entry") == "Hi there"
