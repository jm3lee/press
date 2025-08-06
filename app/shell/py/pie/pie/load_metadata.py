from __future__ import annotations

from pathlib import Path
from typing import Any, Mapping
import warnings

from pie import build_index
from pie.utils import logger


def load_metadata_pair(path: Path) -> Mapping[str, Any] | None:
    """Load metadata from ``path`` and a sibling Markdown/YAML file.

    If both a ``.md`` and ``.yml``/``.yaml`` exist for the same base name,
    the metadata from each file is combined. Values from YAML override those
    from Markdown when keys conflict and a :class:`UserWarning` is emitted.
    Returns ``None`` if neither file contains metadata.
    """

    base = path.with_suffix("")
    md_path = base.with_suffix(".md")
    yml_path = base.with_suffix(".yml")
    yaml_path = base.with_suffix(".yaml")

    md_data = None
    if md_path.exists():
        md_data = build_index.process_markdown(str(md_path))

    yaml_data = None
    yaml_file: Path | None = None
    if yml_path.exists():
        yaml_file = yml_path
        yaml_data = build_index.parse_yaml_metadata(str(yml_path))
    elif yaml_path.exists():
        yaml_file = yaml_path
        yaml_data = build_index.parse_yaml_metadata(str(yaml_path))

    if md_data is None and yaml_data is None:
        return None

    combined: dict[str, Any] = {}
    if md_data:
        combined.update(md_data)
    if yaml_data:
        for k, v in yaml_data.items():
            if k in combined and combined[k] != v:
                warnings.warn(
                    f"Conflict for '{k}', using value from {yaml_file.name}",
                    UserWarning,
                )
            combined[k] = v

    if "id" not in combined:
        base = path.with_suffix("")
        combined["id"] = base.name
        logger.info(
            "Generated 'id'",
            filename=str(path.resolve().relative_to(Path.cwd())),
            id=combined["id"],
        )

    logger.debug(combined)
    return combined
