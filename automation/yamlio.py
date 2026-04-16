from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml


class CatalogDumper(yaml.SafeDumper):
    """Stable YAML dumper for generated catalog artifacts."""


def load_yaml(path: Path) -> dict[str, Any]:
    if not path.exists():
        raise FileNotFoundError(f"Expected YAML file '{path}' to exist.")

    with path.open(encoding="utf-8") as handle:
        payload = yaml.safe_load(handle) or {}

    if not isinstance(payload, dict):
        raise TypeError(f"YAML file '{path}' must contain a mapping at the top level.")

    return payload


def dump_yaml(path: Path, payload: dict[str, Any]) -> None:
    with path.open("w", encoding="utf-8") as handle:
        yaml.dump(
            payload,
            handle,
            Dumper=CatalogDumper,
            sort_keys=False,
            allow_unicode=True,
        )


def _represent_mapping(dumper: CatalogDumper, data: dict[Any, Any]) -> yaml.Node:
    return dumper.represent_mapping("tag:yaml.org,2002:map", data.items())


def _represent_sequence(dumper: CatalogDumper, data: list[Any]) -> yaml.Node:
    return dumper.represent_sequence("tag:yaml.org,2002:seq", data, flow_style=True)


CatalogDumper.add_representer(dict, _represent_mapping)
CatalogDumper.add_representer(list, _represent_sequence)
