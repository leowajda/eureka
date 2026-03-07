import re
import shlex
import subprocess

from action import Action

# Captures the first quoted token in a commit message, e.g. solution(python): 'Two Sum'
QUOTATION_TEXT = r"'([^']*)'"

# Strips any character that is not alphanumeric, a hyphen, or a space.
# Spaces are intentionally preserved here so that a subsequent .replace(" ", "-")
# can convert them to hyphens; removing them first would silently collapse words.
ILLEGAL_SYMBOLS = r"[^a-zA-Z0-9- ]"

# git pretty-format placeholders keyed by semantic name.
# Order matters: the three fields are expected as (timestamp, message, hash).
METADATA = {
    "author_time": "at",
    "commit_message": "B",
    "commit_hash": "H",
}


class Solution:
    def __init__(
        self,
        file_path: str,
        action_type: Action,
        server_url: str,
        repo: str,
    ) -> None:
        self.file_path: str = file_path

        # Initialise all optional attributes to None upfront so every code
        # path leaves the object fully initialised and attribute access never
        # raises AttributeError regardless of which branch is taken below.
        self.problem_name: str | None = None
        self.sha: str | None = None
        self.github_url: str | None = None
        self.host_url: str | None = None

        metadata = Solution.find_metadata(file_path)

        if metadata is None:
            self.action: Action = Action.UNDEFINED
            # Dummy timestamp required so UNDEFINED entries sort last.
            self.timestamp: int = 1_000_000_000
            return

        timestamp, commit, sha = metadata
        self.problem_name = re.findall(QUOTATION_TEXT, commit)[0]
        self.timestamp = int(timestamp)
        self.action = action_type
        self.sha = sha

        # Strip illegal characters first (spaces survive), then convert spaces
        # to hyphens so multi-word names become valid URL path segments.
        dashed_name = (
            re.sub(ILLEGAL_SYMBOLS, "", self.problem_name)
            .replace(" ", "-")
            .lower()
        )
        commit_metadata = re.sub(QUOTATION_TEXT, "", commit).lower()
        emoji = (
            "arrows_counterclockwise"
            if "recursive" in commit_metadata
            else "arrow_right_hook"
        )
        host = (
            "leetcode.com/problems"
            if "leetcode" in commit_metadata
            else "hackerrank.com/challenges"
        )

        self.github_url = f"[:{emoji}:]({server_url}/{repo}/blob/master/{file_path})"
        self.host_url = f"[{self.problem_name}](https://{host}/{dashed_name})"

    @staticmethod
    def find_metadata(path: str) -> tuple[str, str, str] | None:
        """Return (timestamp, message, sha) for *path*, or None if no matching commit."""
        delimiter = len(METADATA)
        options = "%n".join("%" + v for v in METADATA.values())
        quoted_path = shlex.quote(path)

        completed_process = subprocess.run(
            args=(
                f'git log --pretty=format:"{options}" --follow'
                f' --grep="^solution" -- {quoted_path}'
                f" | head -n {delimiter}"
            ),
            text=True,
            check=True,
            shell=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )

        lines = completed_process.stdout.splitlines()
        if len(lines) < delimiter:
            return None

        timestamp, commit, sha = lines[:3]
        return timestamp, commit, sha

    def __str__(self) -> str:
        return " ".join(f"{key}: {value}" for key, value in vars(self).items())

    def __eq__(self, other: object) -> bool:
        if isinstance(other, Solution):
            return str(self) == str(other)
        return NotImplemented

    def __hash__(self) -> int:
        return hash(str(self))
