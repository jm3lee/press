from __future__ import annotations

from pathlib import Path

from pie.create import site


def test_create_scaffolding(tmp_path: Path) -> None:
    target = tmp_path / "press-project"
    site.main([str(target)])

    compose = target / "docker-compose.yml"
    assert compose.exists()
    text = compose.read_text(encoding="utf-8")
    for svc in ["nginx:", "nginx-dev:", "dragonfly:", "shell:"]:
        assert svc in text
    assert "    build: app/shell" in text
    assert '    entrypoint: ["bash"]' in text
    assert "      - ./:/data" in text
    assert "      - ./src/dep.mk:/app/mk/dep.mk" in text
    assert (target / "src").is_dir()

    dep_mk = target / "src/dep.mk"
    assert dep_mk.exists()
    assert dep_mk.read_text(encoding="utf-8") == ""

    robots = target / "src/robots.txt"
    assert robots.exists()
    robots_text = robots.read_text(encoding="utf-8")
    assert "User-agent: *" in robots_text

    assert (target / "redo.mk").exists()

    assert (target / "src/style.css").exists()
    assert (target / "src/pandoc-template.html").exists()

    shell_dockerfile = target / "app/shell/Dockerfile"
    assert shell_dockerfile.exists()
    assert shell_dockerfile.read_text(encoding="utf-8").startswith("FROM press-release")

    index_md = target / "src/index.md"
    assert index_md.exists()
    md_text = index_md.read_text(encoding="utf-8")
    assert "Welcome" in md_text
    assert "view it locally" in md_text

    index_yml = target / "src/index.yml"
    assert index_yml.exists()
    yml_text = index_yml.read_text(encoding="utf-8")
    assert "name:" in yml_text

    readme = target / "README.md"
    assert readme.exists(), "README should be created"
    readme_text = readme.read_text(encoding="utf-8")
    assert "docker-compose build" in readme_text
