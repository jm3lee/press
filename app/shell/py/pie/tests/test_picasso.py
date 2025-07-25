from pathlib import Path

from pie import picasso


def test_generate_rule_basic():
    rule = picasso.generate_rule(Path("src/foo/bar.yml")).strip()
    expected = (
        "build/foo/bar.yml: src/foo/bar.yml\n"
        "\temojify < $< > $@\n"
        "build/foo/bar.html: build/foo/bar.md build/foo/bar.yml\n"
        "\t$(PANDOC_CMD) $(PANDOC_OPTS) --metadata-file=build/foo/bar.yml -o $@ $<\n"
        "\tpython3 -m pie.error_on_python_dict $@"
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
