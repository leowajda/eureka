import re
import subprocess
from action import Action

QUOTATION_TEXT = r"'([^']*)'"

ILLEGAL_SYMBOLS = r"[^a-zA-Z0-9- ]"

METADATA = {
    "author_time": "at",
    "commit_message": "B",
    "commit_hash": "H"
}


class Solution:
    def __init__(self, file_path: str, action_type: Action, server_url: str, repo: str):
        self.file_path = file_path
        metadata = Solution.find_metadata(file_path)

        if not metadata:
            self.action = Action.UNDEFINED
            # dummy timestamp needed for sorting
            self.timestamp = 1_000_000_000
            return

        timestamp, commit, sha = metadata
        self.problem_name, *_ = re.findall(QUOTATION_TEXT, commit)
        self.timestamp = int(timestamp)
        self.action = action_type
        self.sha = sha

        dashed_name = re.sub(ILLEGAL_SYMBOLS, "", self.problem_name).replace(" ", "-").lower()
        commit_metadata = re.sub(QUOTATION_TEXT, "", commit).lower()
        emoji = "arrows_counterclockwise" if 'recursive' in commit_metadata else "arrow_right_hook"
        url = f"https://{'leetcode.com/problems' if 'leetcode' in commit_metadata else 'hackerrank.com/challenges'}"

        self.github_url = f'[:{emoji}:]({server_url}/{repo}/blob/master/{file_path})'
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
        return " ".join(f"{key}: {value}" for key, value in vars(self).items())

    def __eq__(self, other):
        if isinstance(other, Solution):
            return str(self) == str(other)
        return False
