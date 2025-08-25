from __future__ import annotations

from pathlib import Path

from pie.update import url as update_url


def test_renames_files_and_updates_url(tmp_path: Path, monkeypatch, capsys) -> None:
    """Filenames and url fields replace underscores with dashes."""
    src = tmp_path / "src"
    src.mkdir()
    md = src / "hello_world.md"
    md.write_text("---\n---\n", encoding="utf-8")
    yml = src / "hello_world.yml"
    yml.write_text("url: /hello_world/\n", encoding="utf-8")

    monkeypatch.chdir(tmp_path)
    monkeypatch.setattr(
        update_url, "get_changed_files", lambda: [Path("src/hello_world.md")]
    )

    update_url.main([])

    new_md = src / "hello-world.md"
    new_yml = src / "hello-world.yml"
    assert new_md.exists()
    assert new_yml.exists()
    assert "url: /hello-world/" in new_yml.read_text(encoding="utf-8")
    captured = capsys.readouterr()
    assert captured.out == ""
    log_text = (tmp_path / "log/update-url.txt").read_text(encoding="utf-8")
    assert "src/hello_world.md -> src/hello-world.md" in log_text
    assert "src/hello_world.yml -> src/hello-world.yml" in log_text
    assert "src/hello-world.yml: /hello_world/ -> /hello-world/" in log_text
    assert "Summary {'checked': 2, 'changed_count': 3}" in log_text


def test_scans_multiple_paths(tmp_path: Path, monkeypatch) -> None:
    """Multiple paths can be files or directories."""
    src = tmp_path / "src"
    (src / "a").mkdir(parents=True)
    (src / "b").mkdir(parents=True)
    (src / "a" / "hello_world.md").write_text("---\n---\n", encoding="utf-8")
    (src / "a" / "hello_world.yml").write_text(
        "url: /hello_world/\n", encoding="utf-8"
    )
    (src / "b" / "hello_world.md").write_text("---\n---\n", encoding="utf-8")
    (src / "b" / "hello_world.yml").write_text(
        "url: /hello_world/\n", encoding="utf-8"
    )

    monkeypatch.chdir(tmp_path)

    update_url.main(["src/a", "src/b/hello_world.md"])

    for part in ["a", "b"]:
        new_md = src / part / "hello-world.md"
        new_yml = src / part / "hello-world.yml"
        assert new_md.exists()
        assert new_yml.exists()
        assert "url: /hello-world/" in new_yml.read_text(encoding="utf-8")

    log_text = (tmp_path / "log/update-url.txt").read_text(encoding="utf-8")
    assert "src/a/hello_world.md -> src/a/hello-world.md" in log_text
    assert "src/b/hello_world.md -> src/b/hello-world.md" in log_text
    assert "src/a/hello_world.yml -> src/a/hello-world.yml" in log_text
    assert "src/b/hello_world.yml -> src/b/hello-world.yml" in log_text
    assert "src/a/hello-world.yml: /hello_world/ -> /hello-world/" in log_text
    assert "src/b/hello-world.yml: /hello_world/ -> /hello-world/" in log_text
    assert "Summary {'checked': 4, 'changed_count': 6}" in log_text
