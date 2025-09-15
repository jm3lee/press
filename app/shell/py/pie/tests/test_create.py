from __future__ import annotations

from pathlib import Path

import pytest

from pie.create import site


@pytest.fixture()
def scaffold(tmp_path: Path) -> Path:
    target = tmp_path / "press-project"
    site.main([str(target)])
    return target


def test_docker_compose_has_services(scaffold: Path) -> None:
    compose = scaffold / "docker-compose.yml"
    assert compose.exists()
    text = compose.read_text(encoding="utf-8")
    for svc in ["nginx:", "nginx-dev:", "dragonfly:", "shell:"]:
        assert svc in text
    assert "    build: ./app/shell" in text
    assert "    working_dir: /data" in text
    assert '    entrypoint: ["bash"]' in text
    assert "      - ./:/data" in text


def test_generated_files_have_content(scaffold: Path) -> None:
    assert (scaffold / "src").is_dir()

    dep_mk = scaffold / "src/dep.mk"
    assert dep_mk.exists()
    assert dep_mk.read_text(encoding="utf-8") == ""

    robots = scaffold / "src/robots.txt"
    assert robots.exists()
    robots_text = robots.read_text(encoding="utf-8")
    assert "User-agent: *" in robots_text

    redo_mk = scaffold / "redo.mk"
    assert "PYTEST_CMD" in redo_mk.read_text(encoding="utf-8")

    style_css = scaffold / "src/css/style.css"
    style_text = style_css.read_text(encoding="utf-8")
    assert "font-family" in style_text

    template = scaffold / "src/templates/template.html.jinja"
    assert template.exists()
    assert not (scaffold / "src/template.html").exists()

    makefile = scaffold / "makefile"
    assert makefile.exists()
    make_text = makefile.read_text(encoding="utf-8")
    assert "BASE_URL ?= http://press.io" in make_text

    shell_dockerfile = scaffold / "app/shell/Dockerfile"
    assert shell_dockerfile.exists()
    docker_text = shell_dockerfile.read_text(encoding="utf-8")
    assert docker_text.startswith("FROM press-release")

    nginx_dir = scaffold / "app/nginx"
    nginx_dockerfile = nginx_dir / "Dockerfile"
    assert nginx_dockerfile.exists()
    nginx_docker_text = nginx_dockerfile.read_text(encoding="utf-8")
    assert nginx_docker_text.startswith("FROM nginx:alpine-slim")

    dev_conf = nginx_dir / "default.conf"
    assert dev_conf.exists()
    dev_conf_text = dev_conf.read_text(encoding="utf-8")
    assert "include /usr/share/nginx/html/permalinks.conf;" in dev_conf_text

    prod_conf = nginx_dir / "prod.conf"
    assert prod_conf.exists()
    prod_conf_text = prod_conf.read_text(encoding="utf-8")
    assert "server {" in prod_conf_text

    index_md = scaffold / "src/index.md"
    assert index_md.exists()
    md_text = index_md.read_text(encoding="utf-8")
    assert "Welcome" in md_text
    assert "view it locally" in md_text

    index_yml = scaffold / "src/index.yml"
    assert index_yml.exists()
    yml_text = index_yml.read_text(encoding="utf-8")
    assert "title:" in yml_text

    readme = scaffold / "README.md"
    assert readme.exists(), "README should be created"
    readme_text = readme.read_text(encoding="utf-8")
    assert "docker-compose build" in readme_text

    update_author = scaffold / "cfg/update-author.yml"
    assert update_author.exists()
    update_author_text = update_author.read_text(encoding="utf-8")
    assert update_author_text == "doc:\n  author: unknown\n"

    shell_script = scaffold / "bin/shell"
    assert shell_script.exists()
    shell_text = shell_script.read_text(encoding="utf-8")
    assert "docker compose" in shell_text
    assert shell_script.stat().st_mode & 0o111

    redis_cli = scaffold / "bin/redis-cli"
    assert redis_cli.exists()
    redis_text = redis_cli.read_text(encoding="utf-8")
    assert "docker compose exec dragonfly redis-cli" in redis_text
    assert redis_cli.stat().st_mode & 0o111

    upgrade_script = scaffold / "bin/upgrade"
    assert upgrade_script.exists()
    upgrade_text = upgrade_script.read_text(encoding="utf-8")
    assert "Upgrade Build Successful" in upgrade_text
    assert upgrade_script.stat().st_mode & 0o111
