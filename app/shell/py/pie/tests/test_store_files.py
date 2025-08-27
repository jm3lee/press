from __future__ import annotations

from pathlib import Path

from ruamel.yaml import YAML

yaml = YAML(typ="safe")

from pie import store_files


def test_generate_id_length_and_characters() -> None:
    token = store_files.generate_id(12)
    assert len(token) == 12
    assert all(ch in store_files.ALPHABET for ch in token)


def test_iter_files_returns_all_files(tmp_path: Path) -> None:
    (tmp_path / "a.txt").write_text("A")
    sub = tmp_path / "sub"
    sub.mkdir()
    (sub / "b.txt").write_text("B")

    files = sorted(store_files.iter_files(tmp_path))
    assert files == [tmp_path / "a.txt", sub / "b.txt"]

    single = tmp_path / "single.txt"
    single.write_text("S")
    assert list(store_files.iter_files(single)) == [single]


def test_process_file_moves_and_creates_metadata(tmp_path: Path, monkeypatch) -> None:
    src = tmp_path / "file.txt"
    src.write_text("data")
    dest = tmp_path / "dest"
    meta = tmp_path / "meta"

    monkeypatch.setattr(store_files, "generate_id", lambda size=8: "fixedid")

    file_id = store_files.process_file(src, dest, meta)
    assert file_id == "fixedid"

    dest_file = dest / "fixedid"
    meta_file = meta / "fixedid.yml"
    assert dest_file.read_text() == "data"
    expected_yaml = store_files.METADATA_TEMPLATE.render(baseurl="", file_id="fixedid")
    assert meta_file.read_text() == expected_yaml
    meta_data = yaml.load(expected_yaml)
    assert meta_data["id"] == "fixedid"
    assert meta_data["url"] == "/v2/files/0/fixedid"
    assert meta_data["author"] == ""
    assert meta_data["pubdate"] == ""
    assert not src.exists()


def test_process_file_uses_baseurl(tmp_path: Path, monkeypatch) -> None:
    src = tmp_path / "file.txt"
    src.write_text("data")
    dest = tmp_path / "dest"
    meta = tmp_path / "meta"

    monkeypatch.setattr(store_files, "generate_id", lambda size=8: "fixedid")

    store_files.process_file(src, dest, meta, baseurl="https://example.com")
    meta_file = meta / "fixedid.yml"
    meta_data = yaml.load(meta_file.read_text())
    assert meta_data["url"] == "https://example.com/v2/files/0/fixedid"


def test_main_processes_files_with_limit(tmp_path: Path, monkeypatch) -> None:
    one = tmp_path / "one.txt"
    one.write_text("1")
    two = tmp_path / "two.txt"
    two.write_text("2")

    ids = iter(["id1", "id2"])
    monkeypatch.setattr(store_files, "generate_id", lambda size=8: next(ids))
    monkeypatch.chdir(tmp_path)

    store_files.main([str(one), str(two), "-n", "1"])

    dest_dir = Path("s3") / "v2" / "files" / "0"
    meta_dir = Path("src") / "static" / "files"

    assert (dest_dir / "id1").exists()
    assert (meta_dir / "id1.yml").exists()
    assert two.exists()


def test_main_uses_config_file(tmp_path: Path, monkeypatch) -> None:
    base = tmp_path / "input"
    base.mkdir()
    (base / "file.txt").write_text("data")

    cfg = tmp_path / "cfg.yml"
    cfg.write_text("baseurl: https://files.example")

    monkeypatch.setattr(store_files, "generate_id", lambda size=8: "id1")
    monkeypatch.chdir(tmp_path)

    store_files.main([str(base), "--config", str(cfg)])

    meta_file = Path("src") / "static" / "files" / "id1.yml"
    meta_data = yaml.load(meta_file.read_text())
    assert meta_data["url"] == "https://files.example/v2/files/0/id1"


def test_main_errors_on_missing_config(tmp_path: Path, monkeypatch) -> None:
    base = tmp_path / "input"
    base.mkdir()
    (base / "file.txt").write_text("data")

    missing = tmp_path / "missing.yml"
    monkeypatch.chdir(tmp_path)

    rc = store_files.main([str(base), "--config", str(missing)])
    assert rc == 1
