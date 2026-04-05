from __future__ import annotations

from pathlib import Path
import os
import subprocess
from typing import Any

import yaml

ProblemMap = dict[str, dict[str, Any]]
PROBLEM_FIELDS = ("name", "url", "difficulty", "categories")


class ProblemDumper(yaml.SafeDumper):
    pass


ProblemDumper.add_representer(
    dict,
    lambda dumper, data: dumper.represent_mapping(
        "tag:yaml.org,2002:map", data.items()
    ),
)
ProblemDumper.add_representer(
    list,
    lambda dumper, data: dumper.represent_sequence(
        "tag:yaml.org,2002:seq", data, flow_style=True
    ),
)


def require_env(name: str) -> str:
    value = os.getenv(name)
    if value:
        return value
    raise RuntimeError(f"Required environment variable '{name}' is not set or empty.")


def optional_env(name: str) -> str | None:
    return os.getenv(name) or None


def split_env_list(name: str) -> list[str]:
    return (os.getenv(name) or "").split()


def write_output(path: Path, name: str, value: str) -> None:
    with path.open("a", encoding="utf-8") as handle:
        handle.write(f"{name}<<EOF\n{value}\nEOF\n")


def load_problems(path: Path) -> ProblemMap:
    if not path.exists():
        raise RuntimeError(f"Required YAML file '{path}' does not exist.")

    with path.open(encoding="utf-8") as handle:
        return (yaml.safe_load(handle) or {}).get("problems", {})


def dump_problems(path: Path, problems: ProblemMap) -> None:
    with path.open("w", encoding="utf-8") as handle:
        yaml.dump(
            {"problems": problems},
            handle,
            Dumper=ProblemDumper,
            sort_keys=False,
            allow_unicode=True,
        )


def run_git(*args: str, cwd: Path | None = None) -> str:
    return subprocess.run(
        ["git", *args],
        check=True,
        cwd=cwd,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
    ).stdout.strip()


def extract_submodule_sha(raw_status: str) -> str:
    commit_sha, _ = raw_status.split(maxsplit=1)
    return commit_sha.lstrip("+-U")


def merge_problem(existing: dict[str, Any], incoming: dict[str, Any]) -> dict[str, Any]:
    merged = {**existing}

    for field in PROBLEM_FIELDS:
        if field in incoming:
            merged[field] = incoming[field]

    for key, value in incoming.items():
        if key not in PROBLEM_FIELDS and value:
            merged[key] = value

    return merged


def prune_problem(problem: dict[str, Any]) -> dict[str, Any] | None:
    cleaned = {
        key: value for key, value in problem.items() if key in PROBLEM_FIELDS or value
    }
    has_implementations = any(key not in PROBLEM_FIELDS for key in cleaned)
    return cleaned if has_implementations else None


def iter_submodule_dirs(root: Path, prefix: str = "eureka-") -> list[Path]:
    return sorted(
        [
            entry
            for entry in root.iterdir()
            if entry.is_dir() and entry.name.startswith(prefix)
        ],
        key=lambda entry: entry.name,
    )
