from pathlib import Path

from pie.update import link_filters


def test_converts_basic_filters(tmp_path: Path) -> None:
    fp = tmp_path / "example.md"
    fp.write_text('{{ "hull" | link }}\n', encoding="utf-8")
    assert link_filters.process_file(fp)
    assert fp.read_text(encoding="utf-8") == '{{ link("hull") }}\n'


def test_preserves_arguments(tmp_path: Path) -> None:
    fp = tmp_path / "example.md"
    fp.write_text('{{ "hull"|link(style="title") }}', encoding="utf-8")
    link_filters.process_file(fp)
    assert (
        fp.read_text(encoding="utf-8")
        == '{{ link("hull", style="title") }}'
    )
