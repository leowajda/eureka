import os
import shlex
import subprocess
from pathlib import Path

import yaml


def _require_env(name: str) -> str:
    value = os.getenv(name)
    if not value:
        raise RuntimeError(
            f"Required environment variable '{name}' is not set or empty."
        )
    return value


YAML_FILE: Path = Path(_require_env("yaml_file"))
ACTOR = _require_env("actor")
SERVER_URL = _require_env("server_url")
GITHUB_OUTPUT: Path = Path(_require_env("GITHUB_OUTPUT"))

SUBMODULE_PREFIX = "eureka"
REPO_ROOT: Path = Path(".")


def load_yaml(path: Path) -> dict:
    print(f"Loading YAML from: {path}")
    if not path.exists():
        raise RuntimeError(f"Required YAML file '{path}' does not exist.")
    with open(path) as f:
        data = yaml.safe_load(f) or {}
        return data.get("problems", {})


print(f"Loading eureka problems from: {YAML_FILE}")
eureka_problems: dict = load_yaml(YAML_FILE)
original_problems: dict = dict(eureka_problems)

sub_directories: list[Path] = [
    f for f in REPO_ROOT.iterdir() if f.is_dir() and SUBMODULE_PREFIX in f.name
]

print(f"Found {len(sub_directories)} submodules to process")

for directory in sub_directories:
    submodule_yaml: Path = directory / "_data" / "problems.yml"
    print(f"Checking submodule: {directory.name} -> {submodule_yaml}")
    if not submodule_yaml.exists():
        print(f"  Skipping {directory.name}: no _data/problems.yml found")
        continue

    print(f"  Loading YAML from {submodule_yaml}")
    submodule_problems: dict = load_yaml(submodule_yaml)
    lang: str = directory.name.replace("eureka-", "")
    print(f"  Processing {len(submodule_problems)} problems for language: {lang}")

    for slug, problem_data in submodule_problems.items():
        if slug not in eureka_problems:
            print(f"    Adding new problem: {slug}")
            eureka_problems[slug] = {
                "name": problem_data.get("name", ""),
                "url": problem_data.get("url", ""),
                "difficulty": problem_data.get("difficulty", ""),
                "categories": problem_data.get("categories", []),
            }

        lang_data = {
            k: v
            for k, v in problem_data.items()
            if k not in ["name", "url", "difficulty", "categories"]
        }
        if lang_data:
            eureka_problems[slug][lang] = lang_data

if eureka_problems == original_problems:
    print("No changes detected in problems, exiting.")
    raise SystemExit(0)

print(f"Changes detected: {len(eureka_problems)} total problems")

details: list[str] = []
for directory in sub_directories:
    result = subprocess.run(
        args=(
            f"git submodule status {shlex.quote(directory.name)}"
            f" | awk '{{print $1}}'"
            f" | sed 's/^[-+]//'"
        ),
        text=True,
        check=True,
        shell=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    commit_sha = result.stdout.strip()
    details.append(f"{SERVER_URL}/{ACTOR}/{directory.name}/commit/{commit_sha}")

noun = "change" if len(details) == 1 else "changes"
commit_msg = f"ci(docs): update table with latest {noun}\n" + "\n".join(details)

with GITHUB_OUTPUT.open("a") as f:
    print(f"commit_msg<<EOF\n{commit_msg}\nEOF", file=f)

print(f"Writing merged YAML to: {YAML_FILE}")
with YAML_FILE.open("w") as f:
    f.write("problems:\n")
    for slug in sorted(eureka_problems.keys()):
        problem = eureka_problems[slug]
        f.write(f"  {slug}:\n")
        f.write(f"    name: {problem['name']}\n")
        f.write(f"    url: {problem['url']}\n")
        f.write(f"    difficulty: {problem['difficulty']}\n")

        categories = problem.get("categories", [])
        if categories:
            f.write(f"    categories: [{', '.join(categories)}]\n")

        for lang in sorted(
            [
                k
                for k in problem.keys()
                if k not in ["name", "url", "difficulty", "categories"] and problem[k]
            ]
        ):
            f.write(f"    {lang}:\n")
            for approach in ["iterative", "recursive"]:
                if approach in problem[lang]:
                    f.write(f"      {approach}: {problem[lang][approach]}\n")

print("Merge completed successfully.")
