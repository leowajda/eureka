import os
import shlex
import subprocess
from pathlib import Path

import pandas as pd
import yaml


def _require_env(name: str) -> str:
    value = os.getenv(name)
    if not value:
        raise RuntimeError(
            f"Required environment variable '{name}' is not set or empty."
        )
    return value


README: Path = Path(_require_env("readme"))
YAML_FILE: Path = Path(_require_env("yaml_file"))
HEADER: Path = Path(_require_env("header"))
ACTOR = _require_env("actor")
SERVER_URL = _require_env("server_url")
GITHUB_OUTPUT: Path = Path(_require_env("GITHUB_OUTPUT"))

SUBMODULE_PREFIX = "eureka"
REPO_ROOT: Path = Path(".")


def load_yaml(path: Path) -> dict:
    if not path.exists():
        return {"problems": {}}
    with open(path) as f:
        data = yaml.safe_load(f) or {}
        return data.get("problems", {})


eureka_problems: dict = load_yaml(YAML_FILE)
original_problems: dict = dict(eureka_problems)

sub_directories: list[Path] = [
    f for f in REPO_ROOT.iterdir() if f.is_dir() and SUBMODULE_PREFIX in f.name
]

for directory in sub_directories:
    submodule_yaml: Path = directory / "_data" / "problems.yml"
    if not submodule_yaml.exists():
        continue

    submodule_problems: dict = load_yaml(submodule_yaml)
    lang: str = directory.name.replace("eureka-", "")

    for slug, problem_data in submodule_problems.items():
        if slug not in eureka_problems:
            eureka_problems[slug] = {
                "name": problem_data.get("name", ""),
                "url": problem_data.get("url", ""),
                "difficulty": problem_data.get("difficulty", ""),
                "categories": problem_data.get("categories", []),
            }

        eureka_problems[slug][lang] = {
            k: v
            for k, v in problem_data.items()
            if k not in ["name", "url", "difficulty", "categories"]
        }

if eureka_problems == original_problems:
    raise SystemExit(0)

all_langs: set[str] = set()
for problem in eureka_problems.values():
    all_langs.update(
        k
        for k in problem.keys()
        if k not in ["name", "url", "difficulty", "categories"]
    )
langs: list[str] = sorted(all_langs)

table_data: list[dict] = []
for slug in sorted(eureka_problems.keys()):
    problem = eureka_problems[slug]
    row: dict = {"Problem": f"[{problem.get('name', '')}]({problem.get('url', '')})"}
    for lang in langs:
        if lang in problem:
            solutions: list[str] = []
            for approach, url in problem[lang].items():
                emoji: str = (
                    "arrows_counterclockwise"
                    if approach == "recursive"
                    else "arrow_right_hook"
                )
                solutions.append(f"[:{emoji}:]({url})")
            row[lang] = " ".join(solutions)
        else:
            row[lang] = ""
    table_data.append(row)

df: pd.DataFrame = pd.DataFrame(table_data)

header_content: str = HEADER.read_text()
new_readme: str = header_content + "\n\n## Problems\n\n" + df.to_markdown(index=False)

if README.exists() and README.read_text() == new_readme:
    raise SystemExit(0)

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

with YAML_FILE.open("w") as f:
    yaml.dump(
        {"problems": eureka_problems},
        f,
        default_flow_style=False,
        sort_keys=False,
        allow_unicode=True,
    )

with README.open("w") as f:
    f.write(new_readme)
