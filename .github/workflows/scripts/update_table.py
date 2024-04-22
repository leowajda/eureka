import os
import re
import subprocess
import sys
from enum import Enum, unique

import pandas as pd

QUOTATION_TEXT, ILLEGAL_SYMBOLS = r"'([^']*)'", r"[^a-zA-Z0-9- ]"

METADATA = {
    "author_time": "at",
    "commit_message": "B",
    "commit_hash": "H"
}

ADDED_FILES, CHANGED_FILES, REMOVED_FILES = [
    os.getenv(env).split() for env in ("added_files", "changed_files", "removed_files")
]

REPOSITORY, SERVER_URL, README, DATAFRAME, HEADER = [
    os.getenv(env) for env in ("repository", "server_url", "readme", "dataframe", "header")
]


@unique
class Action(str, Enum):
    ADD = "add"
    UPDATE = "update"
    REMOVE = "remove"
    UNDEFINED = "undefined"

    @classmethod
    def _missing_(cls, value: str):
        value = value.lower()
        for member in cls:
            if member.value in value:
                return member
        return Action.UNDEFINED


class Solution:
    def __init__(self, file_path: str, action_type: Action):
        timestamp, commit, sha = Solution.find_metadata(file_path)
        self.problem_name, *_ = re.findall(QUOTATION_TEXT, commit)
        self.timestamp = int(timestamp)
        self.action = action_type
        self.sha = sha

        dashed_name = re.sub(ILLEGAL_SYMBOLS, "", self.problem_name).replace(" ", "-").lower()
        commit_metadata = re.sub(QUOTATION_TEXT, "", commit).lower()
        emoji = "arrows_counterclockwise" if 'recursive' in commit_metadata else "arrow_right_hook"
        url = f"https://{'leetcode.com/problems' if 'leetcode' in commit_metadata else 'hackerrank.com/challenges'}"

        self.github_url = f'[:{emoji}:]({SERVER_URL}/{REPOSITORY}/blob/master/{file_path})'
        self.host_url = f'[{self.problem_name}]({url}/{dashed_name})'

    @staticmethod
    def find_metadata(path: str) -> list[str]:
        delimiter = len(METADATA)
        options = "%n".join("%" + v for v in METADATA.values())

        completed_process = subprocess.run(
            args=f'git log --pretty=format:"{options}" --follow --grep="^solution" -- {path} | head -n {delimiter}',
            text=True, check=True, shell=True, stdout=subprocess.PIPE
        )

        return completed_process.stdout.splitlines()

    def __str__(self):
        match self.action:
            case Action.UNDEFINED:
                return f"{self.action}"
            case _:
                return f"solution: {solution.action} github_url: {self.github_url} host_url: {self.host_url}"


removed_solutions = [Solution(file_path=file, action_type=Action.REMOVE) for file in REMOVED_FILES]
updated_solutions = [Solution(file_path=file, action_type=Action.UPDATE) for file in CHANGED_FILES]
added_solutions = [Solution(file_path=file, action_type=Action.ADD) for file in ADDED_FILES]

df = pd.read_csv(DATAFRAME)
name_col, lang_col = df.columns
df = df.assign(lang_col=df[lang_col].str.split(' '))
df = df.explode(lang_col)

solutions = sorted(removed_solutions + updated_solutions + added_solutions, key=lambda x: x.timestamp)
mod_df = df

for solution in solutions:
    match solution.action:
        case Action.UNDEFINED:
            print("couldn't resolve commit metadata, aborting...")
            sys.exit(1)
        case Action.ADD | Action.UPDATE:
            print(f"{'adding' if solution.action == Action.ADD else 'updating'} {solution}...")
            frame = pd.DataFrame([[solution.host_url, solution.github_url]], columns=[name_col, lang_col])
            mod_df = pd.concat([frame, mod_df], ignore_index=True)
        case Action.REMOVE:
            print(f"removing {solution}...")
            mod_df = mod_df[(mod_df[name_col] != solution.host_url) & (mod_df[lang_col] != solution.github_url)]

mod_df = mod_df.groupby(by=name_col, as_index=False)
mod_df = mod_df[lang_col].agg(lambda x: set(x))
mod_df[lang_col] = mod_df[lang_col].apply(' '.join)

if not mod_df.equals(df):
    with open(os.environ['GITHUB_OUTPUT'], 'a') as f:
        details = [f"{solution.problem_name}: {solution.sha}" for solution in solutions]
        commit_msg = f'ci(docs): update table with changes from {", ".join(details)}'
        print(f"commit_msg={commit_msg}", file=f)

    mod_df = mod_df.set_index(keys=[name_col]).sort_index()
    with open(DATAFRAME, 'w') as f:
        f.write(mod_df.to_csv())

    with open(README, 'w') as f:
        with open(HEADER, 'r') as s:
            content = s.read()
        f.write(content)
        f.write(mod_df.to_markdown(colalign=("center", "center")))
