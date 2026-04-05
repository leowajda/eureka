import os
from operator import attrgetter
from pathlib import Path

import yaml

from action import Action
from solution import Solution


def _require_env(name: str) -> str:
    value = os.getenv(name)
    if not value:
        raise RuntimeError(
            f"Required environment variable '{name}' is not set or empty."
        )
    return value


def _env_filelist(name: str) -> list[str]:
    return (os.getenv(name) or "").split()


ADDED_FILES: list[str] = _env_filelist("added_files")
CHANGED_FILES: list[str] = _env_filelist("changed_files")
REMOVED_FILES: list[str] = _env_filelist("removed_files")

REPOSITORY: str = _require_env("repository")
SERVER_URL: str = _require_env("server_url")
YAML_FILE: Path = Path(_require_env("yaml_file"))
GITHUB_OUTPUT: Path = Path(_require_env("GITHUB_OUTPUT"))


removed_solutions: list[Solution] = [
    Solution(file, Action.REMOVE, SERVER_URL, REPOSITORY) for file in REMOVED_FILES
]
updated_solutions: list[Solution] = [
    Solution(file, Action.UPDATE, SERVER_URL, REPOSITORY) for file in CHANGED_FILES
]
added_solutions: list[Solution] = [
    Solution(file, Action.ADD, SERVER_URL, REPOSITORY) for file in ADDED_FILES
]

all_solutions: list[Solution] = sorted(
    removed_solutions + updated_solutions + added_solutions,
    key=attrgetter("timestamp"),
)


def load_yaml() -> dict:
    print(f"Loading YAML from: {YAML_FILE}")
    if not YAML_FILE.exists():
        raise RuntimeError(f"Required YAML file '{YAML_FILE}' does not exist.")
    with open(YAML_FILE) as f:
        data = yaml.safe_load(f) or {}
        return data.get("problems", {})


print(f"Loading existing problems from: {YAML_FILE}")
original_problems: dict = load_yaml()
modified_problems: dict = dict(original_problems)


active_solutions: list[Solution] = []

for solution in all_solutions:
    if solution.action == Action.UNDEFINED:
        print(f"couldn't resolve commit metadata for {solution}, skipping...")
        continue

    slug = solution.slug
    lang = solution.lang
    approach = solution.approach
    url = solution.github_url.replace(f"[:{solution.emoji}:](", "").rstrip(")")

    if solution.action == Action.REMOVE:
        if slug in modified_problems and lang in modified_problems[slug]:
            if approach in modified_problems[slug][lang]:
                del modified_problems[slug][lang][approach]
                print(f"removed {slug}.{lang}.{approach}")
                active_solutions.append(solution)

    elif solution.action in (Action.ADD, Action.UPDATE):
        if slug not in modified_problems:
            print(f"adding new problem: {slug}")
            modified_problems[slug] = {
                "name": solution.problem_name,
                "url": solution.host_url.split("](")[1].rstrip(")"),
                "difficulty": solution.difficulty,
                "categories": solution.categories,
            }
        if lang not in modified_problems[slug]:
            modified_problems[slug][lang] = {}
        modified_problems[slug][lang][approach] = url
        print(f"{solution.action.value} {slug}.{lang}.{approach}")
        active_solutions.append(solution)


if modified_problems == original_problems:
    print("No changes detected, exiting.")
    raise SystemExit(0)

print(f"Changes detected: {len(active_solutions)} solutions updated")

details: list[str] = [f"{s.problem_name}: {s.sha}" for s in active_solutions]
noun: str = "change" if len(details) == 1 else "changes"
commit_msg: str = f"ci(docs): update table with latest {noun}\n" + "\n".join(details)

with GITHUB_OUTPUT.open("a") as f:
    print(f"commit_msg<<EOF\n{commit_msg}\nEOF", file=f)

print(f"Writing updated YAML to: {YAML_FILE}")
with YAML_FILE.open("w") as f:
    yaml.dump(
        {"problems": modified_problems},
        f,
        default_flow_style=False,
        sort_keys=False,
        allow_unicode=True,
    )

print("Update completed successfully.")
