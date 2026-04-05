from __future__ import annotations

from pathlib import Path

from action import Action
from solution import Solution
from workflow_support import (
    MetadataFetchConfig,
    ScriptContext,
    dump_problems,
    load_problems,
    optional_env,
    prune_problem_entry,
    require_env,
    split_env_list,
    write_output,
)


def collect_solutions(config: MetadataFetchConfig) -> list[Solution]:
    pending: list[Solution] = []

    for action, files in (
        (Action.REMOVE, split_env_list("removed_files")),
        (Action.UPDATE, split_env_list("changed_files")),
        (Action.ADD, split_env_list("added_files")),
    ):
        for file_path in files:
            solution = Solution.from_file(file_path, action, config)
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


def build_commit_message(solutions: list[Solution]) -> str:
    details = [f"{solution.problem_name}: {solution.sha}" for solution in solutions]
    noun = "change" if len(details) == 1 else "changes"
    return f"ci(docs): update table with latest {noun}\n" + "\n".join(details)


def main() -> None:
    context = ScriptContext(
        yaml_file=Path(require_env("yaml_file")),
        github_output=Path(require_env("GITHUB_OUTPUT")),
    )
    config = MetadataFetchConfig(
        server_url=require_env("server_url"),
        repository=require_env("repository"),
        leetcode_session=optional_env("LEETCODE_SESSION"),
    )

    original_problems = load_problems(context.yaml_file)
    updated_problems = dict(original_problems)

    changed_solutions: list[Solution] = []
    for solution in collect_solutions(config):
        if apply_solution_change(updated_problems, solution):
            changed_solutions.append(solution)

    if updated_problems == original_problems:
        raise SystemExit(0)

    dump_problems(context.yaml_file, updated_problems)
    write_output(
        context.github_output, "commit_msg", build_commit_message(changed_solutions)
    )


if __name__ == "__main__":
    main()
