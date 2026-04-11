from __future__ import annotations

from pathlib import Path

from workflow_support import (
    PROBLEM_FIELDS,
    dump_problem_table,
    extract_submodule_sha,
    iter_submodule_dirs,
    load_languages,
    load_problems,
    merge_problem,
    require_env,
    run_git,
    write_output,
)

SUBMODULE_PREFIX = "eureka-"


def merge_submodule_problems(root: Path, problems: dict[str, dict]) -> dict[str, dict]:
    merged = dict(problems)

    for directory in iter_submodule_dirs(root, SUBMODULE_PREFIX):
        submodule_yaml = directory / "_data" / "problems.yml"
        if not submodule_yaml.exists():
            continue

        language = directory.name.removeprefix(SUBMODULE_PREFIX)
        submodule_problems = load_problems(submodule_yaml)

        for slug, problem_data in submodule_problems.items():
            existing = merged.get(slug, {})
            incoming = {
                field: problem_data.get(
                    field,
                    existing.get(field, [] if field == "categories" else ""),
                )
                for field in PROBLEM_FIELDS
            }
            implementations = {
                key: value
                for key, value in problem_data.items()
                if key not in PROBLEM_FIELDS and value
            }
            if implementations:
                incoming[language] = implementations

            merged[slug] = merge_problem(existing, incoming)

    return merged


def default_language_label(language: str) -> str:
    parts = [part for part in language.replace("_", "-").split("-") if part]
    if not parts:
        return language

    return " ".join(
        part.upper() if part.isalpha() and len(part) <= 3 else part.capitalize()
        for part in parts
    )


def collect_languages(
    root: Path, existing_languages: dict[str, dict[str, str]]
) -> dict[str, dict[str, str]]:
    languages: dict[str, dict[str, str]] = {}

    for directory in iter_submodule_dirs(root, SUBMODULE_PREFIX):
        submodule_yaml = directory / "_data" / "problems.yml"
        if not submodule_yaml.exists():
            continue

        language = directory.name.removeprefix(SUBMODULE_PREFIX)
        defaults = {
            "label": default_language_label(language),
            "code_language": language,
        }
        existing = existing_languages.get(language, {})
        languages[language] = {
            **defaults,
            **{
                key: value
                for key, value in existing.items()
                if isinstance(value, str) and value
            },
        }

    return languages


def collect_submodule_details(root: Path, actor: str, server_url: str) -> list[str]:
    details = []
    for directory in iter_submodule_dirs(root, SUBMODULE_PREFIX):
        raw_status = run_git("submodule", "status", "--", directory.name, cwd=root)
        if not raw_status:
            continue
        details.append(
            f"{server_url}/{actor}/{directory.name}/commit/{extract_submodule_sha(raw_status)}"
        )
    return details


def main() -> None:
    root = Path(".")
    yaml_file = Path(require_env("yaml_file"))
    github_output = Path(require_env("GITHUB_OUTPUT"))
    actor = require_env("actor")
    server_url = require_env("server_url")

    original_languages = load_languages(yaml_file)
    original_problems = load_problems(yaml_file)
    merged_languages = collect_languages(root, original_languages)
    merged_problems = merge_submodule_problems(root, original_problems)
    if merged_languages == original_languages and merged_problems == original_problems:
        raise SystemExit(0)

    dump_problem_table(yaml_file, merged_problems, merged_languages)

    details = collect_submodule_details(root, actor, server_url)
    noun = "change" if len(details) == 1 else "changes"
    write_output(
        github_output,
        "commit_msg",
        f"ci(docs): update table with latest {noun}\n" + "\n".join(details),
    )


if __name__ == "__main__":
    main()
