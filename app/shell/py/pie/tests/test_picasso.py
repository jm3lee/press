from pathlib import Path

from pie import picasso


def test_generate_rule_basic():
    rule = picasso.generate_rule(Path("src/foo/bar.yml")).strip()
    expected = (
        "build/foo/bar.yml: src/foo/bar.yml\n"
        "\t$(Q)mkdir -p $(dir build/foo/bar.yml)\n"
        "\t$(Q)emojify < $< > $@\n"
        "\t$(Q)process-yaml $< $@\n"
        "build/foo/bar.html: build/foo/bar.md build/foo/bar.yml\n"
        "\t$(Q)$(PANDOC_CMD) $(PANDOC_OPTS) --metadata-file=build/foo/bar.yml -o $@ $<\n"
        "\t$(Q)check-html-for-python-dicts $@"
    )
    assert rule == expected


def test_main_prints_rules(tmp_path, capsys):
    src = tmp_path / "src"
    build = tmp_path / "build"
    src.mkdir()
    (src / "doc.yml").write_text("{}")

    picasso.main(["--src", str(src), "--build", str(build)])
    out = capsys.readouterr().out.strip()
    expected = picasso.generate_rule(src / "doc.yml", src_root=src, build_root=build).strip()
    assert out == expected


def test_main_writes_log_file(tmp_path):
    src = tmp_path / "src"
    build = tmp_path / "build"
    src.mkdir()
    (src / "doc.yml").write_text("{}")
    log = tmp_path / "picasso.log"

    picasso.main(["--src", str(src), "--build", str(build), "--log", str(log)])

    assert log.exists()


def test_generate_dependencies(tmp_path):
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
