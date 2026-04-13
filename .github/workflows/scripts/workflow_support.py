from __future__ import annotations

from dataclasses import dataclass
from fnmatch import fnmatchcase
import os
from pathlib import Path
import subprocess
from typing import Any

import yaml

ProblemMap = dict[str, dict[str, Any]]
LanguageMap = dict[str, dict[str, str]]
PROBLEM_FIELDS = ("name", "url", "difficulty", "categories")


@dataclass(frozen=True)
class LanguageTarget:
    language: str
    label: str
    code_language: str
    path_prefix: str
    path_glob: str
    source_url_base: str

    @classmethod
    def from_env(cls) -> LanguageTarget:
        return cls(
            language=require_env("TARGET_LANGUAGE"),
            label=require_env("TARGET_LABEL"),
            code_language=require_env("TARGET_CODE_LANGUAGE"),
            path_prefix=normalize_path(require_env("TARGET_PATH_PREFIX")),
            path_glob=normalize_path(require_env("TARGET_PATH_GLOB")),
            source_url_base=require_env("SOURCE_URL_BASE").rstrip("/"),
        )

    def matches(self, file_path: str) -> bool:
        normalized = normalize_path(file_path)
        return normalized.startswith(f"{self.path_prefix}/") and fnmatchcase(
            normalized, self.path_glob
        )

    def source_url(self, file_path: str) -> str:
        return f"{self.source_url_base}/{normalize_path(file_path)}"


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
    return [
        normalize_path(value)
        for value in (os.getenv(name) or "").splitlines()
        if value.strip()
    ]


def load_problem_table(path: Path) -> dict[str, Any]:
    if not path.exists():
        raise RuntimeError(f"Required YAML file '{path}' does not exist.")

    with path.open(encoding="utf-8") as handle:
        payload = yaml.safe_load(handle) or {}
        return payload if isinstance(payload, dict) else {}


def load_languages(path: Path) -> LanguageMap:
    payload = load_problem_table(path)
    languages = payload.get("languages", {})
    return languages if isinstance(languages, dict) else {}


def load_problems(path: Path) -> ProblemMap:
    payload = load_problem_table(path)
    problems = payload.get("problems", {})
    return problems if isinstance(problems, dict) else {}


def dump_problems(path: Path, problems: ProblemMap) -> None:
    payload = load_problem_table(path)
    languages = payload.get("languages")
    dump_problem_table(
        path, problems, languages if isinstance(languages, dict) else None
    )


def dump_problem_table(
    path: Path, problems: ProblemMap, languages: LanguageMap | None = None
) -> None:
    payload: dict[str, Any] = {}
    if languages:
        payload["languages"] = languages
    payload["problems"] = problems

    with path.open("w", encoding="utf-8") as handle:
        yaml.dump(
            payload,
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


def prune_problem(problem: dict[str, Any]) -> dict[str, Any] | None:
    cleaned = {
        key: value for key, value in problem.items() if key in PROBLEM_FIELDS or value
    }
    has_implementations = any(key not in PROBLEM_FIELDS for key in cleaned)
    return cleaned if has_implementations else None


def prune_problem_entry(problem: dict[str, Any]) -> dict[str, Any] | None:
    return prune_problem(problem)


def normalize_path(path: str) -> str:
    return path.strip().replace("\\", "/").removeprefix("./")


def remove_language_implementations(
    problems: ProblemMap, language: str
) -> ProblemMap:
    cleaned: ProblemMap = {}
    for slug, problem in problems.items():
        updated = dict(problem)
        updated.pop(language, None)
        pruned = prune_problem(updated)
        if pruned is not None:
            cleaned[slug] = pruned
    return cleaned


def upsert_language_metadata(
    languages: LanguageMap, target: LanguageTarget
) -> LanguageMap:
    updated = dict(languages)
    existing = dict(updated.get(target.language, {}))
    existing["label"] = target.label
    existing["code_language"] = target.code_language
    updated[target.language] = existing
    return updated
