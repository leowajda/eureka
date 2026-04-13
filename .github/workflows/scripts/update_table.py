from __future__ import annotations

from pathlib import Path

from action import Action
from solution import Solution
from workflow_support import (
    LanguageTarget,
    dump_problem_table,
    load_problems,
    load_languages,
    optional_env,
    remove_language_implementations,
    prune_problem_entry,
    require_env,
    split_env_list,
    upsert_language_metadata,
)

REPLAY_MODE = "replay"
INCREMENTAL_MODE = "incremental"


def collect_solutions(
    *, target: LanguageTarget, sync_mode: str, leetcode_session: str | None
) -> list[Solution]:
    pending: list[Solution] = []

    sources = (
        ((Action.ADD, split_env_list("CURRENT_FILES")),)
        if sync_mode == REPLAY_MODE
        else (
            (Action.REMOVE, split_env_list("REMOVED_FILES")),
            (Action.UPDATE, split_env_list("CHANGED_FILES")),
            (Action.ADD, split_env_list("ADDED_FILES")),
        )
    )

    for action, files in sources:
        for file_path in files:
            if not target.matches(file_path):
                continue
            solution = Solution.from_file(
                file_path,
                action,
                target=target,
                leetcode_session=leetcode_session,
            )
            if solution is not None:
                pending.append(solution)

    return sorted(pending, key=lambda solution: solution.timestamp)


def apply_solution_change(problems: dict[str, dict], solution: Solution) -> bool:
    problem = dict(problems.get(solution.slug, {}))
    implementations = dict(problem.get(solution.language, {}))

    if solution.action is Action.REMOVE:
        if solution.approach not in implementations:
            return False
        del implementations[solution.approach]
    else:
        if not problem:
            problem = {
                "name": solution.problem_name,
                "url": solution.problem_url,
                "difficulty": solution.difficulty,
                "categories": list(solution.categories),
            }
        implementations[solution.approach] = solution.source_url

    if implementations:
        problem[solution.language] = implementations
    else:
        problem.pop(solution.language, None)

    cleaned = prune_problem_entry(problem)
    if cleaned is None:
        problems.pop(solution.slug, None)
    else:
        problems[solution.slug] = cleaned

    return True


def require_sync_mode() -> str:
    sync_mode = require_env("SYNC_MODE")
    if sync_mode not in {INCREMENTAL_MODE, REPLAY_MODE}:
        raise RuntimeError(
            f"Unsupported sync mode {sync_mode!r}; expected '{INCREMENTAL_MODE}' or '{REPLAY_MODE}'."
        )
    return sync_mode


def main() -> None:
    yaml_file = Path(require_env("YAML_FILE"))
    sync_mode = require_sync_mode()
    target = LanguageTarget.from_env()
    leetcode_session = optional_env("LEETCODE_SESSION")

    original_languages = load_languages(yaml_file)
    original_problems = load_problems(yaml_file)
    updated_languages = upsert_language_metadata(original_languages, target)
    updated_problems = (
        remove_language_implementations(original_problems, target.language)
        if sync_mode == REPLAY_MODE
        else dict(original_problems)
    )

    for solution in collect_solutions(
        target=target,
        sync_mode=sync_mode,
        leetcode_session=leetcode_session,
    ):
        apply_solution_change(updated_problems, solution)

    if updated_languages == original_languages and updated_problems == original_problems:
        raise SystemExit(0)

    dump_problem_table(yaml_file, updated_problems, updated_languages)


if __name__ == "__main__":
    main()
