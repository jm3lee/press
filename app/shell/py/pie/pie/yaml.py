from __future__ import annotations

from pathlib import Path
from typing import Any

from ruamel.yaml import YAML

from pie.logging import logger

# Shared YAML handler configured for project defaults
yaml = YAML(typ="safe")
yaml.allow_unicode = True
yaml.sort_keys = False
yaml.default_flow_style = False

# Extensions recognised as YAML files
YAML_EXTS = {".yml", ".yaml"}


def read_yaml(filename: str | Path):
    """Return YAML-decoded data from *filename*."""

    logger.debug("Reading YAML", filename=str(filename))
    with open(filename, "r", encoding="utf-8") as f:
        return yaml.load(f)


def write_yaml(data: Any, filename: str | Path) -> None:
    """Write *data* as YAML to *filename*."""

    logger.debug("Writing YAML", filename=str(filename))
    with open(filename, "w", encoding="utf-8") as f:
        yaml.dump(data, f)
