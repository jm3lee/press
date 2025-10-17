"""Configuration loading for the Flashoffer CLI."""

from __future__ import annotations

from dataclasses import dataclass
import json
import os
from pathlib import Path
from typing import Dict, Iterable, List


@dataclass(frozen=True)
class ServiceConfig:
    """Represents configuration for a docker-compose backed service."""

    name: str
    compose_files: List[str]
    shared_services: List[str]
    image: str
    remote_suffix: str
    supports_install: bool
    supports_npm: bool
    supports_coverage: bool
    post_build_install: bool
    npm_workdir: str | None = None

    def compose_env_value(self) -> str:
        """Return the colon-separated compose file list."""

        return ":".join(self.compose_files)

    def default_remote_image(self, registry: str) -> str:
        """Build the default remote image path for pushes."""

        return f"{registry}/{self.remote_suffix}"


@dataclass(frozen=True)
class CLIConfig:
    """Root configuration for the Flashoffer CLI."""

    registry_env: str
    registry_default: str
    services: Dict[str, ServiceConfig]

    def allowed_services(self, names: Iterable[str] | None = None) -> Dict[str, ServiceConfig]:
        """Return a filtered set of services if ``names`` is provided."""

        if names is None:
            return self.services
        subset = {name: self.services[name] for name in names}
        return subset

    def registry(self) -> str:
        """Resolve the registry value from the environment."""

        return os.environ.get(self.registry_env, self.registry_default)


def _load_services(raw_services: Dict[str, object]) -> Dict[str, ServiceConfig]:
    services: Dict[str, ServiceConfig] = {}
    for name, raw_config in raw_services.items():
        if not isinstance(raw_config, dict):
            raise ValueError(f"Invalid configuration for service {name!r}")
        compose_files = _require_list(raw_config, "compose_files")
        shared_services = _require_list(raw_config, "shared_services")
        image = _require_str(raw_config, "image")
        remote_suffix = _require_str(raw_config, "remote_suffix")
        supports = raw_config.get("supports", {})
        if not isinstance(supports, dict):
            raise ValueError(f"Invalid supports block for {name!r}")
        npm_workdir = raw_config.get("npm_workdir")
        if npm_workdir is not None and not isinstance(npm_workdir, str):
            raise ValueError(f"npm_workdir must be a string for {name!r}")
        services[name] = ServiceConfig(
            name=name,
            compose_files=compose_files,
            shared_services=shared_services,
            image=image,
            remote_suffix=remote_suffix,
            supports_install=bool(supports.get("install", False)),
            supports_npm=bool(supports.get("npm", False)),
            supports_coverage=bool(supports.get("coverage", False)),
            post_build_install=bool(supports.get("post_build_install", False)),
            npm_workdir=npm_workdir,
        )
    return services


def _require_list(raw_config: Dict[str, object], key: str) -> List[str]:
    value = raw_config.get(key)
    if not isinstance(value, list) or not all(isinstance(item, str) for item in value):
        raise ValueError(f"{key} must be a list of strings")
    return value


def _require_str(raw_config: Dict[str, object], key: str) -> str:
    value = raw_config.get(key)
    if not isinstance(value, str):
        raise ValueError(f"{key} must be a string")
    return value


def load_config(path: Path) -> CLIConfig:
    """Load configuration data from ``path``."""

    with path.open("r", encoding="utf-8") as handle:
        raw_data = json.load(handle)
    registry_env = raw_data.get("registry_env")
    registry_default = raw_data.get("registry_default")
    raw_services = raw_data.get("services")
    if not isinstance(registry_env, str) or not registry_env:
        raise ValueError("registry_env must be a non-empty string")
    if not isinstance(registry_default, str) or not registry_default:
        raise ValueError("registry_default must be a non-empty string")
    if not isinstance(raw_services, dict) or not raw_services:
        raise ValueError("services must be a non-empty mapping")
    services = _load_services(raw_services)
    return CLIConfig(
        registry_env=registry_env,
        registry_default=registry_default,
        services=services,
    )
