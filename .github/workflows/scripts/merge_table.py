from __future__ import annotations

from pathlib import Path

from workflow_support import (
    PROBLEM_FIELDS,
    dump_problems,
    extract_submodule_sha,
    iter_submodule_dirs,
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

    original_problems = load_problems(yaml_file)
    merged_problems = merge_submodule_problems(root, original_problems)
    if merged_problems == original_problems:
        raise SystemExit(0)

    dump_problems(yaml_file, merged_problems)

    details = collect_submodule_details(root, actor, server_url)
    noun = "change" if len(details) == 1 else "changes"
    write_output(
        github_output,
        "commit_msg",
        f"ci(docs): update table with latest {noun}\n" + "\n".join(details),
    )


if __name__ == "__main__":
    main()
