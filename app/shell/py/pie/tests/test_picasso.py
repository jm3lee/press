from pathlib import Path
import runpy
import sys

import pytest
from pie.build import picasso


def test_generate_rule_basic(tmp_path, monkeypatch):
    """generate_rule('src/foo/bar.yml') -> build/foo/bar.{yml,html} rule."""
    src = tmp_path / "src" / "foo"
    src.mkdir(parents=True)
    (src / "bar.yml").write_text("{}")
    monkeypatch.chdir(tmp_path)
    monkeypatch.setattr(picasso, "load_metadata_pair", lambda path: None)
    rule = picasso.generate_rule(Path("src/foo/bar.yml")).strip()
    expected = (
        "build/foo/bar.yml: src/foo/bar.yml\n"
        "\t$(call status,Preprocess $<)\n"
        "\t$(Q)mkdir -p $(dir build/foo/bar.yml)\n"
        "\t$(Q)cp $< $@\n"
        "build/foo/bar.html: build/foo/bar.md build/foo/bar.yml $(HTML_TEMPLATE) $(BUILD_DIR)/.process-yamls\n"
        "\t$(call status,Generate HTML $@)\n"
        "\t$(Q)render-html build/foo/bar.md build/foo/bar.yml $@"
    )
    assert rule == expected
    assert "render-html" in rule



def test_generate_rule_with_template(tmp_path, monkeypatch):
    """Custom template -> rule includes specific template."""
    src = tmp_path / "src" / "foo"
    src.mkdir(parents=True)
    template = tmp_path / "src" / "templates" / "blog" / "template.html.jinja"
    template.parent.mkdir(parents=True, exist_ok=True)
    template.write_text("tmpl")
    (src / "bar.yml").write_text("{}")
    monkeypatch.chdir(tmp_path)
    monkeypatch.setattr(
        picasso,
        "load_metadata_pair",
        lambda path: {"template": "src/templates/blog/template.html.jinja"},
    )
    rule = picasso.generate_rule(Path("src/foo/bar.yml")).strip()
    expected = (
        "build/foo/bar.yml: src/foo/bar.yml\n"
        "\t$(call status,Preprocess $<)\n"
        "\t$(Q)mkdir -p $(dir build/foo/bar.yml)\n"
        "\t$(Q)cp $< $@\n"
        "build/foo/bar.html: build/foo/bar.md build/foo/bar.yml src/templates/blog/template.html.jinja $(BUILD_DIR)/.process-yamls\n"
        "\t$(call status,Generate HTML $@)\n"
        "\t$(Q)render-html build/foo/bar.md build/foo/bar.yml $@"
    )
    assert rule == expected
    assert "render-html" in rule


def test_main_prints_rules(tmp_path, capsys, monkeypatch):
    """CLI prints rule for doc.yml."""
    src = tmp_path / "src"
    build = tmp_path / "build"
    src.mkdir()
    (src / "doc.yml").write_text("{}")

    monkeypatch.setattr(picasso, "load_metadata_pair", lambda path: None)
    picasso.main(["--src", str(src), "--build", str(build)])
    out = capsys.readouterr().out.strip()
    expected = picasso.generate_rule(src / "doc.yml", src_root=src, build_root=build).strip()
    assert out == expected



def test_main_writes_log_file(tmp_path, monkeypatch):
    """--log writes picasso.log."""
    src = tmp_path / "src"
    build = tmp_path / "build"
    src.mkdir()
    (src / "doc.yml").write_text("{}")
    log = tmp_path / "picasso.log"

    monkeypatch.setattr(picasso, "load_metadata_pair", lambda path: None)
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


def test_generate_dependencies_link_global(tmp_path):
    """{{link("quickstart")}} -> build/index.md: build/quickstart.md."""
    src = tmp_path / "src"
    build = tmp_path / "build"
    src.mkdir()

    quick = src / "quickstart.md"
    quick.write_text("---\nid: quickstart\n---\nbody")

    index = src / "index.md"
    index.write_text('{{link("quickstart")}}')

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


def test_resolve_include_paths_directory(tmp_path):
    """_resolve_include_paths handles directory arguments."""
    src = tmp_path / "src"
    build = tmp_path / "build"
    src.mkdir()

    defs = src / "defs"
    defs.mkdir()
    (defs / "a.md").write_text("a")
    (defs / "b.md").write_text("b")

    index = src / "index.md"
    index.write_text("body")

    def build_path(p: Path) -> str:
        rel = p.relative_to(src)
        out = build / rel
        if build.is_absolute():
            out = Path(build.name) / rel
        return out.as_posix()

    src_build = Path(build_path(index)).with_suffix(index.suffix)
    rules = picasso._resolve_include_paths(
        "include",
        "'defs'",
        src_build=src_build,
        src_root=src,
        build_root=build,
        build_path=build_path,
    )

    assert sorted(rules) == [
        "build/index.md: build/defs/a.md",
        "build/index.md: build/defs/b.md",
    ]


def test_resolve_include_paths_glob(tmp_path):
    """_resolve_include_paths applies glob patterns."""
    src = tmp_path / "src"
    build = tmp_path / "build"
    src.mkdir()

    defs = src / "defs"
    defs.mkdir()
    (defs / "a.md").write_text("a")
    (defs / "b.txt").write_text("b")

    index = src / "index.md"
    index.write_text("body")

    def build_path(p: Path) -> str:
        rel = p.relative_to(src)
        out = build / rel
        if build.is_absolute():
            out = Path(build.name) / rel
        return out.as_posix()

    src_build = Path(build_path(index)).with_suffix(index.suffix)
    rules = picasso._resolve_include_paths(
        "include_deflist_entry",
        "'defs', glob='*.md'",
        src_build=src_build,
        src_root=src,
        build_root=build,
        build_path=build_path,
    )

    assert rules == ["build/index.md: build/defs/a.md"]


def test_resolve_include_paths_absolute(tmp_path):
    """Absolute paths are returned unchanged."""
    src = tmp_path / "src"
    build = tmp_path / "build"
    src.mkdir()

    ext = tmp_path / "ext"
    ext.mkdir()
    (ext / "x.md").write_text("x")

    index = src / "index.md"
    index.write_text("body")

    def build_path(p: Path) -> str:
        rel = p.relative_to(src)
        out = build / rel
        if build.is_absolute():
            out = Path(build.name) / rel
        return out.as_posix()

    src_build = Path(build_path(index)).with_suffix(index.suffix)
    rules = picasso._resolve_include_paths(
        "include",
        f"'{ext.as_posix()}'",
        src_build=src_build,
        src_root=src,
        build_root=build,
        build_path=build_path,
    )

    expected = f"build/index.md: {(ext / 'x.md').as_posix()}"
    assert rules == [expected]


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


def test_main_errors_on_missing_directory(tmp_path, monkeypatch):
    """Missing src dir -> SystemExit 1."""
    build = tmp_path / "build"
    monkeypatch.setattr(picasso, "load_metadata_pair", lambda path: None)
    with pytest.raises(SystemExit) as exc:
        picasso.main(["--src", str(tmp_path / "missing"), "--build", str(build)])
    assert exc.value.code == 1


def test_main_prints_dependencies(tmp_path, capsys, monkeypatch):
    """main prints build/index.md: build/quickstart.md."""
    src = tmp_path / "src"
    build = tmp_path / "build"
    src.mkdir()

    quick = src / "quickstart.md"
    quick.write_text("---\nid: quickstart\n---\nbody")
    index = src / "index.md"
    index.write_text('{{"quickstart"|link}}')

    monkeypatch.setattr(picasso, "load_metadata_pair", lambda path: None)
    picasso.main(["--src", str(src), "--build", str(build)])
    out = capsys.readouterr().out
    assert "build/index.md: build/quickstart.md" in out
