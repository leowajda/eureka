from __future__ import annotations

from dataclasses import dataclass
import os
from pathlib import Path
import subprocess
from typing import Any

import yaml

PROBLEM_FIELDS = ("name", "url", "difficulty", "categories")


class ProblemDumper(yaml.SafeDumper):
    pass


def _dict_representer(dumper: yaml.SafeDumper, data: dict[str, Any]) -> yaml.Node:
    return dumper.represent_mapping("tag:yaml.org,2002:map", data.items())


def _list_representer(dumper: yaml.SafeDumper, data: list[Any]) -> yaml.Node:
    return dumper.represent_sequence("tag:yaml.org,2002:seq", data, flow_style=True)


ProblemDumper.add_representer(dict, _dict_representer)
ProblemDumper.add_representer(list, _list_representer)


def require_env(name: str) -> str:
    value = os.getenv(name)
    if not value:
        raise RuntimeError(
            f"Required environment variable '{name}' is not set or empty."
        )
    return value


def optional_env(name: str) -> str | None:
    value = os.getenv(name)
    return value or None


def split_env_list(name: str) -> list[str]:
    return [item for item in (os.getenv(name) or "").split() if item]


def write_output(path: Path, name: str, value: str) -> None:
    with path.open("a", encoding="utf-8") as handle:
        print(f"{name}<<EOF\n{value}\nEOF", file=handle)


def load_problems(path: Path) -> dict[str, dict[str, Any]]:
    if not path.exists():
        raise RuntimeError(f"Required YAML file '{path}' does not exist.")

    with path.open(encoding="utf-8") as handle:
        payload = yaml.safe_load(handle) or {}

    return payload.get("problems", {})


def dump_problems(path: Path, problems: dict[str, dict[str, Any]]) -> None:
    with path.open("w", encoding="utf-8") as handle:
        yaml.dump(
            {"problems": problems},
            handle,
            Dumper=ProblemDumper,
            sort_keys=False,
            allow_unicode=True,
        )


def run_git(*args: str, cwd: Path | None = None) -> str:
    result = subprocess.run(
        ["git", *args],
        check=True,
        cwd=cwd,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
    )
    return result.stdout.strip()


def extract_submodule_sha(raw_status: str) -> str:
    return raw_status.split(maxsplit=1)[0].lstrip("-+")


def merge_problem_entry(
    existing: dict[str, Any], incoming: dict[str, Any]
) -> dict[str, Any]:
    merged = dict(existing)

    for field in PROBLEM_FIELDS:
        if field in incoming:
            merged[field] = incoming[field]

    for language, implementations in incoming.items():
        if language in PROBLEM_FIELDS:
            continue
        if implementations:
            merged[language] = implementations

    return merged


def prune_problem_entry(problem: dict[str, Any]) -> dict[str, Any] | None:
    cleaned = {
        key: value for key, value in problem.items() if key in PROBLEM_FIELDS or value
    }
    implementation_keys = [key for key in cleaned if key not in PROBLEM_FIELDS]
    return cleaned if implementation_keys else None


@dataclass(frozen=True)
class MetadataFetchConfig:
    server_url: str
    repository: str
    leetcode_session: str | None = None


@dataclass(frozen=True)
class ScriptContext:
    yaml_file: Path
    github_output: Path
