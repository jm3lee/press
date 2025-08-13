from __future__ import annotations

from pathlib import Path
import sys

from pie.update import author as update_author


def test_skips_files_outside_src(tmp_path: Path, monkeypatch, capsys) -> None:
    """Files outside src are ignored when no paths are provided."""
    src = tmp_path / "src"
    src.mkdir()
    md = src / "doc.md"
    md.write_text("---\ntitle: Test\n---\n", encoding="utf-8")
    yml = src / "doc.yml"
    yml.write_text("title: Test\nauthor: Jane Doe\n", encoding="utf-8")
    other = tmp_path / "docs"
    other.mkdir()
    other_md = other / "doc.md"
    other_md.write_text("---\ntitle: Other\n---\n", encoding="utf-8")

    cfg = tmp_path / "cfg"
    cfg.mkdir()
    (cfg / "update-author.yml").write_text("author: Brian Lee\n", encoding="utf-8")

    monkeypatch.chdir(tmp_path)
    monkeypatch.setattr(
        update_author,
        "get_changed_files",
        lambda: [Path("src/doc.md"), Path("docs/doc.md")],
    )

    update_author.main([])
    assert "author: Brian Lee" in md.read_text(encoding="utf-8")
    assert "author: Brian Lee" in yml.read_text(encoding="utf-8")
    assert "author" not in other_md.read_text(encoding="utf-8")
    lines = capsys.readouterr().out.strip().splitlines()
    assert "docs/doc.md" not in "".join(lines)


def test_updates_yaml_from_markdown_change(tmp_path: Path, monkeypatch, capsys) -> None:
    """Changing Markdown updates author in paired YAML."""
    src = tmp_path / "src"
    src.mkdir()
    md = src / "doc.md"
    md.write_text("---\ntitle: Test\n---\n", encoding="utf-8")
    yml = src / "doc.yml"
    yml.write_text(
        "title: Test\nauthor: Jane Doe\n",
        encoding="utf-8",
    )

    cfg = tmp_path / "cfg"
    cfg.mkdir()
    (cfg / "update-author.yml").write_text("author: Brian Lee\n", encoding="utf-8")

    monkeypatch.chdir(tmp_path)
    monkeypatch.setattr(update_author, "get_changed_files", lambda: [Path("src/doc.md")])

    update_author.main([])
    assert "author: Brian Lee" in yml.read_text(encoding="utf-8")
    assert "author: Brian Lee" in md.read_text(encoding="utf-8")
    captured = capsys.readouterr()
    lines = captured.out.strip().splitlines()
    assert "src/doc.md: undefined -> Brian Lee" in lines
    assert "src/doc.yml: Jane Doe -> Brian Lee" in lines
    assert "2 files checked" in lines
    assert "2 files changed" in lines
    assert len(lines) == 4
    log_text = (tmp_path / "log/update-author.txt").read_text(encoding="utf-8")
    assert "src/doc.md: undefined -> Brian Lee" in log_text
    assert "src/doc.yml: Jane Doe -> Brian Lee" in log_text


def test_updates_markdown_frontmatter(tmp_path: Path, monkeypatch, capsys) -> None:
    """Author in Markdown frontmatter is replaced."""
    src = tmp_path / "src"
    src.mkdir()
    md = src / "doc.md"
    md.write_text(
        "---\ntitle: Test\nauthor: Jane Doe\n---\nbody\n",
        encoding="utf-8",
    )

    cfg = tmp_path / "cfg"
    cfg.mkdir()
    (cfg / "update-author.yml").write_text("author: Brian Lee\n", encoding="utf-8")

    monkeypatch.chdir(tmp_path)
    monkeypatch.setattr(update_author, "get_changed_files", lambda: [Path("src/doc.md")])

    update_author.main([])
    assert "author: Brian Lee" in md.read_text(encoding="utf-8")
    expected_line = "src/doc.md: Jane Doe -> Brian Lee"
    captured = capsys.readouterr()
    assert captured.out.strip().splitlines() == [
        expected_line,
        "1 file checked",
        "1 file changed",
    ]
    log_text = (tmp_path / "log/update-author.txt").read_text(encoding="utf-8")
    assert expected_line in log_text


def test_adds_frontmatter_when_author_in_body(tmp_path: Path, monkeypatch, capsys) -> None:
    """Author outside frontmatter is ignored and field added to frontmatter."""
    src = tmp_path / "src"
    src.mkdir()
    md = src / "doc.md"
    md.write_text("---\ntitle: Test\n---\nbody\nauthor: Jane Doe\n", encoding="utf-8")

    cfg = tmp_path / "cfg"
    cfg.mkdir()
    (cfg / "update-author.yml").write_text("author: Brian Lee\n", encoding="utf-8")

    monkeypatch.chdir(tmp_path)
    monkeypatch.setattr(update_author, "get_changed_files", lambda: [Path("src/doc.md")])

    update_author.main([])
    text = md.read_text(encoding="utf-8")
    assert "author: Brian Lee" in text
    assert "author: Jane Doe" in text
    captured = capsys.readouterr()
    lines = captured.out.strip().splitlines()
    assert lines == [
        "src/doc.md: undefined -> Brian Lee",
        "1 file checked",
        "1 file changed",
    ]


def test_adds_metadata_when_missing(tmp_path: Path, monkeypatch, capsys) -> None:
    """Frontmatter with author is created when metadata is absent."""
    src = tmp_path / "src"
    src.mkdir()
    md = src / "doc.md"
    md.write_text("body\n", encoding="utf-8")

    cfg = tmp_path / "cfg"
    cfg.mkdir()
    (cfg / "update-author.yml").write_text("author: Brian Lee\n", encoding="utf-8")

    monkeypatch.chdir(tmp_path)
    monkeypatch.setattr(update_author, "get_changed_files", lambda: [Path("src/doc.md")])

    update_author.main([])
    assert md.read_text(encoding="utf-8").startswith("---\nauthor: Brian Lee\n---\n")
    captured = capsys.readouterr()
    assert captured.out.strip().splitlines() == [
        "src/doc.md: undefined -> Brian Lee",
        "1 file checked",
        "1 file changed",
    ]


def test_scans_directory(tmp_path: Path, monkeypatch, capsys) -> None:
    """Specifying a directory scans files without git."""
    src = tmp_path / "src"
    src.mkdir()
    md = src / "doc.md"
    md.write_text("---\ntitle: Test\n---\n", encoding="utf-8")
    yml = src / "doc.yml"
    yml.write_text("title: Test\nauthor: Jane Doe\n", encoding="utf-8")
    yaml_file = src / "other.yaml"
    yaml_file.write_text("title: Test\nauthor: Jane Doe\n", encoding="utf-8")

    cfg = tmp_path / "cfg"
    cfg.mkdir()
    (cfg / "update-author.yml").write_text("author: Brian Lee\n", encoding="utf-8")

    monkeypatch.chdir(tmp_path)

    update_author.main(["src"])
    assert "author: Brian Lee" in yml.read_text(encoding="utf-8")
    assert "author: Brian Lee" in md.read_text(encoding="utf-8")
    assert "author: Brian Lee" in yaml_file.read_text(encoding="utf-8")
    captured = capsys.readouterr()
    lines = captured.out.strip().splitlines()
    assert "src/doc.md: undefined -> Brian Lee" in lines
    assert "src/doc.yml: Jane Doe -> Brian Lee" in lines
    assert "src/other.yaml: Jane Doe -> Brian Lee" in lines
    assert "3 files checked" in lines
    assert "3 files changed" in lines
    assert len(lines) == 5
    log_text = (tmp_path / "log/update-author.txt").read_text(encoding="utf-8")
    assert "src/doc.md: undefined -> Brian Lee" in log_text
    assert "src/doc.yml: Jane Doe -> Brian Lee" in log_text
    assert "src/other.yaml: Jane Doe -> Brian Lee" in log_text


def test_scans_file(tmp_path: Path, monkeypatch, capsys) -> None:
    """Specifying a file scans only that file without git."""
    src = tmp_path / "src"
    src.mkdir()
    md = src / "doc.md"
    md.write_text("---\ntitle: Test\n---\n", encoding="utf-8")
    yml = src / "doc.yml"
    yml.write_text("title: Test\nauthor: Jane Doe\n", encoding="utf-8")

    cfg = tmp_path / "cfg"
    cfg.mkdir()
    (cfg / "update-author.yml").write_text("author: Brian Lee\n", encoding="utf-8")

    monkeypatch.chdir(tmp_path)

    update_author.main(["src/doc.md"])
    assert "author: Brian Lee" in yml.read_text(encoding="utf-8")
    assert "author: Brian Lee" in md.read_text(encoding="utf-8")
    captured = capsys.readouterr()
    lines = captured.out.strip().splitlines()
    assert "src/doc.md: undefined -> Brian Lee" in lines
    assert "src/doc.yml: Jane Doe -> Brian Lee" in lines
    assert "2 files checked" in lines
    assert "2 files changed" in lines
    assert len(lines) == 4
    log_text = (tmp_path / "log/update-author.txt").read_text(encoding="utf-8")
    assert "src/doc.md: undefined -> Brian Lee" in log_text
    assert "src/doc.yml: Jane Doe -> Brian Lee" in log_text


def test_overrides_author_argument(tmp_path: Path, monkeypatch, capsys) -> None:
    """Command line author overrides config value."""
    src = tmp_path / "src"
    src.mkdir()
    md = src / "doc.md"
    md.write_text("---\ntitle: Test\n---\n", encoding="utf-8")
    yml = src / "doc.yml"
    yml.write_text("title: Test\nauthor: Jane Doe\n", encoding="utf-8")

    cfg = tmp_path / "cfg"
    cfg.mkdir()
    (cfg / "update-author.yml").write_text("author: Brian Lee\n", encoding="utf-8")

    monkeypatch.chdir(tmp_path)
    monkeypatch.setattr(update_author, "get_changed_files", lambda: [Path("src/doc.md")])

    update_author.main(["-a", "Chris R."])
    assert "author: Chris R." in yml.read_text(encoding="utf-8")
    assert "author: Chris R." in md.read_text(encoding="utf-8")
    captured = capsys.readouterr()
    lines = captured.out.strip().splitlines()
    assert "src/doc.md: undefined -> Chris R." in lines
    assert "src/doc.yml: Jane Doe -> Chris R." in lines
    assert "2 files checked" in lines
    assert "2 files changed" in lines
    assert len(lines) == 4
    log_text = (tmp_path / "log/update-author.txt").read_text(encoding="utf-8")
    assert "src/doc.md: undefined -> Chris R." in log_text
    assert "src/doc.yml: Jane Doe -> Chris R." in log_text


def test_verbose_enables_debug_logging(tmp_path: Path, monkeypatch) -> None:
    """-v sets the console log level to DEBUG."""
    src = tmp_path / "src"
    src.mkdir()
    (src / "doc.md").write_text("---\ntitle: Test\n---\n", encoding="utf-8")
    (src / "doc.yml").write_text("title: Test\nauthor: Jane Doe\n", encoding="utf-8")

    cfg = tmp_path / "cfg"
    cfg.mkdir()
    (cfg / "update-author.yml").write_text("author: Brian Lee\n", encoding="utf-8")

    monkeypatch.chdir(tmp_path)

    levels: list[str | None] = []
    original_add = update_author.logger.add

    def fake_add(*args, **kwargs):
        levels.append(kwargs.get("level"))
        return original_add(*args, **kwargs)

    monkeypatch.setattr(update_author.logger, "add", fake_add)

    update_author.main(["-v", "src"])

    assert "DEBUG" in levels

    update_author.logger.remove()
    from pie.logging import LOG_FORMAT

    update_author.logger.add(sys.stderr, format=LOG_FORMAT, level="INFO")


def test_scans_multiple_paths(tmp_path: Path, monkeypatch, capsys) -> None:
    """Multiple paths can be files or directories."""
    src = tmp_path / "src"
    (src / "a").mkdir(parents=True)
    (src / "b").mkdir(parents=True)
    (src / "a" / "doc.md").write_text("---\ntitle: A\n---\n", encoding="utf-8")
    (src / "a" / "doc.yml").write_text("title: A\nauthor: Jane Doe\n", encoding="utf-8")
    (src / "b" / "doc.md").write_text("---\ntitle: B\n---\n", encoding="utf-8")
    (src / "b" / "doc.yml").write_text("title: B\nauthor: Jane Doe\n", encoding="utf-8")

    cfg = tmp_path / "cfg"
    cfg.mkdir()
    (cfg / "update-author.yml").write_text("author: Brian Lee\n", encoding="utf-8")

    monkeypatch.chdir(tmp_path)

    update_author.main(["src/a", "src/b/doc.md"])

    for part in ["a", "b"]:
        assert "author: Brian Lee" in (src / part / "doc.md").read_text(encoding="utf-8")
        assert "author: Brian Lee" in (src / part / "doc.yml").read_text(encoding="utf-8")

    lines = capsys.readouterr().out.strip().splitlines()
    assert "4 files checked" in lines
    assert "4 files changed" in lines


def test_accepts_glob_patterns(tmp_path: Path, monkeypatch, capsys) -> None:
    """Glob patterns are expanded before scanning."""
    src = tmp_path / "src"
    (src / "a1").mkdir(parents=True)
    (src / "a2").mkdir(parents=True)
    for part in ["a1", "a2"]:
        (src / part / "doc.md").write_text("---\ntitle: Test\n---\n", encoding="utf-8")
        (src / part / "doc.yml").write_text(
            "title: Test\nauthor: Jane Doe\n", encoding="utf-8"
        )

    cfg = tmp_path / "cfg"
    cfg.mkdir()
    (cfg / "update-author.yml").write_text("author: Brian Lee\n", encoding="utf-8")

    monkeypatch.chdir(tmp_path)

    update_author.main(["src/a*/doc.md"])

    for part in ["a1", "a2"]:
        assert "author: Brian Lee" in (src / part / "doc.md").read_text(encoding="utf-8")
        assert "author: Brian Lee" in (src / part / "doc.yml").read_text(encoding="utf-8")

    lines = capsys.readouterr().out.strip().splitlines()
    assert "4 files checked" in lines
    assert "4 files changed" in lines


def test_verbose_enables_debug_logging(tmp_path: Path, monkeypatch) -> None:
    """-v sets the console log level to DEBUG."""
    src = tmp_path / "src"
    src.mkdir()
    (src / "doc.md").write_text("---\ntitle: Test\n---\n", encoding="utf-8")
    (src / "doc.yml").write_text("title: Test\nauthor: Jane Doe\n", encoding="utf-8")

    cfg = tmp_path / "cfg"
    cfg.mkdir()
    (cfg / "update-author.yml").write_text("author: Brian Lee\n", encoding="utf-8")

    monkeypatch.chdir(tmp_path)

    levels: list[str | None] = []
    original_add = update_author.logger.add

    def fake_add(*args, **kwargs):
        levels.append(kwargs.get("level"))
        return original_add(*args, **kwargs)

    monkeypatch.setattr(update_author.logger, "add", fake_add)

    update_author.main(["-v", "src"])

    assert "DEBUG" in levels

    update_author.logger.remove()
    from pie.logging import LOG_FORMAT

    update_author.logger.add(sys.stderr, format=LOG_FORMAT, level="INFO")

