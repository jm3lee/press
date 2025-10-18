from __future__ import annotations

from pathlib import Path
import sys

import pytest

ROOT_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT_DIR / "src"))

from flashoffer_cli.config import CLIConfig, ServiceConfig, load_config


CONFIG_PATH = Path(__file__).resolve().parents[1] / "cfg" / "flashoffer-cli.json"


@pytest.fixture(scope="module")
def cli_config() -> CLIConfig:
    return load_config(CONFIG_PATH)


def test_quiz_manager_service_present(cli_config: CLIConfig) -> None:
    assert "quiz-manager" in cli_config.services
    service = cli_config.services["quiz-manager"]
    assert isinstance(service, ServiceConfig)
    assert service.compose_files == ["docker-compose.yml"]
    assert service.shared_services == ["quiz-backend"]
    assert service.image == "press-quiz-manager"
    assert service.remote_suffix == "quiz-manager"
    assert service.supports_npm is True
    assert service.supports_install is True
    assert service.npm_workdir == "/app"


def test_allowed_services_filters(cli_config: CLIConfig) -> None:
    subset = cli_config.allowed_services(["quiz-manager"])
    assert list(subset.keys()) == ["quiz-manager"]
    assert subset["quiz-manager"].name == "quiz-manager"
