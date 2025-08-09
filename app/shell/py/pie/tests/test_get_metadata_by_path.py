from pie import metadata


class DummyRedis:
    def __init__(self, store):
        self.store = store

    def get(self, key):
        return self.store.get(key)


def test_returns_value(monkeypatch):
    store = {"/doc.yml": "doc1", "doc1.title": "Title"}
    monkeypatch.setattr(metadata, "redis_conn", DummyRedis(store))
    assert metadata.get_metadata_by_path("/doc.yml", "title") == "Title"


def test_missing_entries(monkeypatch):
    store = {"/doc.yml": "doc1"}
    monkeypatch.setattr(metadata, "redis_conn", DummyRedis(store))
    assert metadata.get_metadata_by_path("/doc.yml", "title") is None
    monkeypatch.setattr(metadata, "redis_conn", DummyRedis({}))
    assert metadata.get_metadata_by_path("/other.yml", "title") is None
