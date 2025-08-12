from pathlib import Path
import runpy
import sys

import pytest
from pie.build import picasso


def test_generate_rule_basic():
    """generate_rule('src/foo/bar.yml') -> build/foo/bar.{yml,html} rule."""
    rule = picasso.generate_rule(Path("src/foo/bar.yml")).strip()
    expected = (
        "build/foo/bar.yml: src/foo/bar.yml\n"
        "\t$(Q)mkdir -p $(dir build/foo/bar.yml)\n"
        "\t$(Q)emojify < $< > $@\n"
        "\t$(Q)render-jinja-template $@ $@\n"
        "build/foo/bar.html: build/foo/bar.md build/foo/bar.yml\n"
        "\t$(Q)$(PANDOC_CMD) $(PANDOC_OPTS) --metadata-file=build/foo/bar.yml -o $@ $<\n"
        "\t$(Q)check-bad-jinja-output $@"
    )
    assert rule == expected


def test_main_prints_rules(tmp_path, capsys):
    """CLI prints rule for doc.yml."""
    src = tmp_path / "src"
    build = tmp_path / "build"
    src.mkdir()
    (src / "doc.yml").write_text("{}")

    picasso.main(["--src", str(src), "--build", str(build)])
    out = capsys.readouterr().out.strip()
    expected = picasso.generate_rule(src / "doc.yml", src_root=src, build_root=build).strip()
    assert out == expected


def test_main_writes_log_file(tmp_path):
    """--log writes picasso.log."""
    src = tmp_path / "src"
    build = tmp_path / "build"
    src.mkdir()
    (src / "doc.yml").write_text("{}")
    log = tmp_path / "picasso.log"

    picasso.main(["--src", str(src), "--build", str(build), "--log", str(log)])

    assert log.exists()


def test_generate_dependencies(tmp_path):
    """link to 'quickstart' -> build/index.md: build/quickstart.md."""
    src = tmp_path / "src"
    build = tmp_path / "build"
    src.mkdir()

    quick = src / "quickstart.md"
    quick.write_text("---\nid: quickstart\n---\nbody")

    index = src / "index.md"
    index.write_text('{{"quickstart"|link}}')

    deps = picasso.generate_dependencies(src, build)

    assert deps == ["build/index.md: build/quickstart.md"]


def test_dependencies_from_include_filter(tmp_path):
    """include('src/inc.md') -> build/index.md: build/inc.md."""
    src = tmp_path / "src"
    build = tmp_path / "build"
    src.mkdir()

    inc = src / "inc.md"
    inc.write_text("body")

    main = src / "index.md"
    main.write_text("```python\ninclude('src/inc.md')\n```\n")

    deps = picasso.generate_dependencies(src, build)

    assert deps == ["build/index.md: build/inc.md"]


def test_circular_dependencies_are_removed(tmp_path):
    """Circular links a<->b -> only a:b and warning."""
    src = tmp_path / "src"
    build = tmp_path / "build"
    src.mkdir()

    a = src / "a.md"
    a.write_text("---\nid: a\n---\n{{\"b\"|link}}")
    b = src / "b.md"
    b.write_text("---\nid: b\n---\n{{\"a\"|link}}")

    messages: list[str] = []
    handle = picasso.logger.add(messages.append, level="WARNING")
    try:
        deps = picasso.generate_dependencies(src, build)
    finally:
        picasso.logger.remove(handle)

    assert deps == ["build/a.md: build/b.md"]
    assert any("Circular dependency detected" in m for m in messages)


def test_collect_ids_invalid_yaml(tmp_path):
    """Malformed YAML still yields id in set."""
    src = tmp_path / "src"
    src.mkdir()
    (src / "bad.yml").write_text(":\n- [")

    ids = picasso.collect_ids(src)

    assert "bad" in ids


def test_collect_ids_uses_metadata_and_skips_duplicates(tmp_path, monkeypatch):
    """Metadata ``id`` is used and `.md`/`.yml` pairs are deduplicated."""
    src = tmp_path / "src"
    src.mkdir()
    monkeypatch.chdir(tmp_path)
    (src / "doc.yml").write_text("id: spam\nurl: /doc.html\n")
    (src / "doc.md").write_text("content")

    ids = picasso.collect_ids(src)

    assert len(ids) == 1
    assert "spam" in ids


def test_has_path_seen_returns_false():
    """_has_path({}, 'a','b',{'a'}) -> False."""
    assert picasso._has_path({}, "a", "b", {"a"}) is False


def test_remove_circular_dependencies_no_colon():
    """'_remove_circular_dependencies({'phony','a: b'})' preserves phony."""
    rules = {"phony", "a: b"}
    result = picasso._remove_circular_dependencies(rules)
    assert result == ["a: b", "phony"]


def test_generate_dependencies_skips_other_extensions(tmp_path):
    """note.txt in src -> no dependencies."""
    src = tmp_path / "src"
    build = tmp_path / "build"
    src.mkdir()
    (src / "note.txt").write_text("ignore")

    deps = picasso.generate_dependencies(src, build)

    assert deps == []


def test_generate_dependencies_logs_read_error(tmp_path, monkeypatch):
    """Read failure -> empty deps."""
    src = tmp_path / "src"
    build = tmp_path / "build"
    src.mkdir()
    bad = src / "bad.md"
    bad.write_text("body")

    original = Path.read_text

    def fake_read_text(self, *args, **kwargs):
        if self.name == "bad.md":
            raise OSError("fail")
        return original(self, *args, **kwargs)

    monkeypatch.setattr(Path, "read_text", fake_read_text)

    deps = picasso.generate_dependencies(src, build)

    assert deps == []


def test_generate_dependencies_ignores_missing_id(tmp_path):
    """link to missing id -> no deps."""
    src = tmp_path / "src"
    build = tmp_path / "build"
    src.mkdir()

    index = src / "index.md"
    index.write_text('{{"missing"|link}}')

    deps = picasso.generate_dependencies(src, build)

    assert deps == []


def test_generate_dependencies_handles_syntax_error(tmp_path):
    """Bad include syntax -> no deps."""
    src = tmp_path / "src"
    build = tmp_path / "build"
    src.mkdir()

    main = src / "index.md"
    main.write_text("```python\ninclude('a', bad=)\n```\n")

    deps = picasso.generate_dependencies(src, build)

    assert deps == []


def test_include_deflist_entry_with_glob_and_directory(tmp_path):
    """include_deflist_entry('defs', glob='*.md') -> deps for each file."""
    src = tmp_path / "src"
    build = tmp_path / "build"
    src.mkdir()

    defs = src / "defs"
    defs.mkdir()
    (defs / "a.md").write_text("a")
    (defs / "b.md").write_text("b")

    index = src / "index.md"
    index.write_text("```python\ninclude_deflist_entry('defs', glob='*.md')\n```\n")

    deps = picasso.generate_dependencies(src, build)

    assert sorted(deps) == [
        "build/index.md: build/defs/a.md",
        "build/index.md: build/defs/b.md",
    ]


def test_include_with_absolute_directory(tmp_path):
    """include('/abs/path') -> dependency uses absolute path."""
    src = tmp_path / "src"
    build = tmp_path / "build"
    src.mkdir()

    ext = tmp_path / "ext"
    ext.mkdir()
    (ext / "x.md").write_text("x")

    index = src / "index.md"
    index.write_text(f"```python\ninclude('{ext.as_posix()}')\n```\n")

    deps = picasso.generate_dependencies(src, build)

    expected = f"build/index.md: {(ext / 'x.md').as_posix()}"
    assert deps == [expected]


def test_main_errors_on_missing_directory(tmp_path):
    """Missing src dir -> SystemExit 1."""
    build = tmp_path / "build"
    with pytest.raises(SystemExit) as exc:
        picasso.main(["--src", str(tmp_path / "missing"), "--build", str(build)])
    assert exc.value.code == 1


def test_main_prints_dependencies(tmp_path, capsys):
    """main prints build/index.md: build/quickstart.md."""
    src = tmp_path / "src"
    build = tmp_path / "build"
    src.mkdir()

    quick = src / "quickstart.md"
    quick.write_text("---\nid: quickstart\n---\nbody")
    index = src / "index.md"
    index.write_text('{{"quickstart"|link}}')

    picasso.main(["--src", str(src), "--build", str(build)])
    out = capsys.readouterr().out
    assert "build/index.md: build/quickstart.md" in out


def test_run_as_module_executes_main(tmp_path, monkeypatch, capsys):
    """runpy.run_path executes picasso.main."""
    src = tmp_path / "src"
    build = tmp_path / "build"
    src.mkdir()
    (src / "doc.yml").write_text("{}")

    argv = [str(picasso.__file__), "--src", str(src), "--build", str(build)]
    monkeypatch.setattr(sys, "argv", argv)
    runpy.run_path(picasso.__file__, run_name="__main__")

    out = capsys.readouterr().out
    assert "build/doc.yml" in out
