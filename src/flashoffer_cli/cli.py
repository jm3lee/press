"""Command-line interface for Flashoffer developer tooling."""

from __future__ import annotations

import argparse
import os
import shutil
import subprocess
import sys
from pathlib import Path
from typing import Iterable, List

from .config import ServiceConfig, load_config

ROOT_DIR = Path(__file__).resolve().parents[2]
CONFIG_PATH = ROOT_DIR / "cfg" / "flashoffer-cli.json"


class CLIError(RuntimeError):
    """Raised when user-facing errors occur in the CLI."""


def _ensure_docker() -> None:
    if shutil.which("docker") is None:
        raise CLIError("docker must be installed to run these commands")


def _set_compose_env(config: ServiceConfig) -> None:
    if "COMPOSE_FILE" not in os.environ:
        os.environ["COMPOSE_FILE"] = config.compose_env_value()


def _compose_base_args(command: str) -> List[str]:
    args = ["docker", "compose", command]
    if command == "up":
        args.append("--remove-orphans")
    return args


def _run_subprocess(args: List[str]) -> None:
    subprocess.run(args, check=True)


def _compose_services_args(config: ServiceConfig) -> List[str]:
    return [*config.shared_services, config.name]


def _run_compose_command(command: str, config: ServiceConfig, extra: List[str]) -> None:
    _ensure_docker()
    args = _compose_base_args(command)
    args.extend(extra)
    args.extend(_compose_services_args(config))
    _run_subprocess(args)


def _host_user_id() -> str:
    return str(os.getuid())


def _run_install(config: ServiceConfig) -> None:
    if not config.supports_install:
        raise CLIError(f"install is not available for the {config.name} service")
    _ensure_docker()
    args = [
        "docker",
        "compose",
        "run",
        "--rm",
        "--entrypoint",
        "npm",
        "-u",
        _host_user_id(),
        config.name,
        "install",
    ]
    _run_subprocess(args)


def _run_npm(config: ServiceConfig, npm_args: List[str]) -> None:
    if not config.supports_npm:
        raise CLIError(f"npm commands are not available for the {config.name} service")
    if not npm_args:
        raise CLIError("npm command requires arguments")
    _ensure_docker()
    args = [
        "docker",
        "compose",
        "run",
        "--rm",
        "--entrypoint",
        "npm",
        "-u",
        _host_user_id(),
    ]
    if config.npm_workdir:
        args.extend(["--workdir", config.npm_workdir])
    args.append(config.name)
    args.extend(npm_args)
    _run_subprocess(args)


def _run_cov(config: ServiceConfig) -> None:
    if not config.supports_coverage:
        raise CLIError(f"cov command is not available for the {config.name} service")
    _run_npm(config, ["run", "test:coverage"])


def _run_bash(config: ServiceConfig) -> None:
    _ensure_docker()
    args = [
        "docker",
        "compose",
        "run",
        "--entrypoint",
        "bash",
        "--rm",
        "--remove-orphans",
        config.name,
    ]
    _run_subprocess(args)


def _run_push(config: ServiceConfig, registry: str, args: List[str]) -> None:
    parser = argparse.ArgumentParser(prog="push", add_help=False)
    parser.add_argument("--tag", dest="tag", help="Remote image tag")
    opts, leftovers = parser.parse_known_args(args)
    if leftovers:
        raise CLIError(f"Unknown push option(s): {' '.join(leftovers)}")
    remote = opts.tag or config.default_remote_image(registry)
    _ensure_docker()
    _run_subprocess(["docker", "tag", config.image, remote])
    _run_subprocess(["docker", "push", remote])


def _normalize_command_args(args: List[str]) -> List[str]:
    if args and args[0] == "--":
        return args[1:]
    return args


def _build_parser(program_name: str, allow_prod: bool, services: Iterable[str]) -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog=program_name,
        description=(
            "Management script for Flashoffer services backed by Docker Compose. "
            "Use --list-services to inspect available service profiles."
        ),
    )
    parser.add_argument(
        "--service",
        choices=sorted(services),
        help="Target a specific service profile",
    )
    if allow_prod:
        parser.add_argument(
            "--prod",
            action="store_true",
            help="Shortcut for --service flashoffer",
        )
    parser.add_argument(
        "--list-services",
        action="store_true",
        help="List the configured service profiles",
    )
    parser.add_argument(
        "command",
        nargs="?",
        default="up",
        help="Command to run (default: up)",
    )
    parser.add_argument(
        "command_args",
        nargs=argparse.REMAINDER,
        help="Additional arguments passed to the underlying command",
    )
    return parser


def main(
    argv: List[str] | None = None,
    *,
    default_service: str = "flashoffer-dev",
    allow_prod_switch: bool = True,
    allowed_services: Iterable[str] | None = None,
    program_name: str | None = None,
) -> int:
    """Entry point for the Flashoffer CLI."""

    config = load_config(CONFIG_PATH)
    services_config = config.allowed_services(allowed_services)
    if default_service not in services_config:
        raise CLIError(f"Unknown default service {default_service!r}")
    program = program_name or Path(sys.argv[0]).name
    parser = _build_parser(program, allow_prod_switch, services_config)
    args = parser.parse_args(argv)

    if args.list_services:
        for name in services_config:
            print(name)
        return 0

    service_name = args.service or default_service
    if allow_prod_switch and getattr(args, "prod", False):
        if service_name not in {default_service, "flashoffer-dev"}:
            raise CLIError("--prod cannot be combined with an explicit --service value")
        service_name = "flashoffer"
    elif args.command == "help":
        parser.print_help()
        return 0
    elif args.command in {"-h", "--help"}:
        parser.print_help()
        return 0
    if not allow_prod_switch and getattr(args, "prod", False):
        raise CLIError("--prod is not supported for this command")

    if service_name not in services_config:
        raise CLIError(f"Unknown service: {service_name}")
    service_config = services_config[service_name]

    os.chdir(ROOT_DIR)
    _set_compose_env(service_config)

    command_args = _normalize_command_args(args.command_args or [])

    registry = config.registry()

    if args.command == "up":
        _run_compose_command("up", service_config, command_args)
        return 0
    if args.command == "build":
        _run_compose_command("build", service_config, command_args)
        if service_config.post_build_install and service_config.supports_install:
            _run_install(service_config)
        return 0
    if args.command == "install":
        _run_install(service_config)
        return 0
    if args.command == "cov":
        _run_cov(service_config)
        return 0
    if args.command == "npm":
        _run_npm(service_config, command_args)
        return 0
    if args.command == "bash":
        _run_bash(service_config)
        return 0
    if args.command == "push":
        _run_push(service_config, registry, command_args)
        return 0
    if args.command in {"help", "-h", "--help"}:
        parser.print_help()
        return 0

    raise CLIError(f"Unknown command: {args.command}")


if __name__ == "__main__":  # pragma: no cover - script entry
    try:
        raise SystemExit(main())
    except CLIError as exc:  # pragma: no cover - CLI error handling
        print(f"Error: {exc}", file=sys.stderr)
        raise SystemExit(1) from exc
