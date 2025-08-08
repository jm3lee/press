from __future__ import annotations

from pathlib import Path

from pie import create


def test_create_scaffolding(tmp_path: Path) -> None:
    target = tmp_path / "press-project"
    create.main([str(target)])

    assert (target / "docker-compose.yml").exists()
    assert (target / "src").is_dir()

    readme = target / "README.md"
    assert readme.exists(), "README should be created"
    text = readme.read_text(encoding="utf-8")
    assert "docker-compose build" in text
