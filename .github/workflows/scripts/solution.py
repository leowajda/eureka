from __future__ import annotations

from dataclasses import dataclass
import re
from typing import Self

import requests

from action import Action
from workflow_support import MetadataFetchConfig, run_git

QUOTED_TITLE = re.compile(r"'([^']+)'")
ILLEGAL_SYMBOLS = re.compile(r"[^a-zA-Z0-9- ]")
LEETCODE_QUERY = {
    "query": "query questionData($titleSlug: String!) { question(titleSlug: $titleSlug) { difficulty topicTags { name } } }",
}


@dataclass(frozen=True)
class CommitMetadata:
    timestamp: int
    message: str
    sha: str


@dataclass(frozen=True)
class ProblemMetadata:
    difficulty: str = ""
    categories: tuple[str, ...] = ()


@dataclass(frozen=True)
class Solution:
    file_path: str
    action: Action
    timestamp: int
    sha: str
    problem_name: str
    slug: str
    source_url: str
    problem_url: str
    approach: str
    language: str
    difficulty: str = ""
    categories: tuple[str, ...] = ()

    @classmethod
    def from_file(
        cls,
        file_path: str,
        action: Action,
        config: MetadataFetchConfig,
    ) -> Self | None:
        metadata = find_metadata(file_path)
        if metadata is None:
            return None

        problem_name = extract_problem_name(metadata.message)
        slug = slugify(problem_name)
        approach = (
            "recursive" if "recursive" in metadata.message.lower() else "iterative"
        )
        language = config.repository.rsplit("/", maxsplit=1)[-1].replace("eureka-", "")
        problem_host = (
            "leetcode.com/problems"
            if "leetcode" in metadata.message.lower()
            else "hackerrank.com/challenges"
        )

        problem_metadata = fetch_problem_metadata(slug, config.leetcode_session)

        return cls(
            file_path=file_path,
            action=action,
            timestamp=metadata.timestamp,
            sha=metadata.sha,
            problem_name=problem_name,
            slug=slug,
            source_url=f"{config.server_url}/{config.repository}/blob/master/{file_path}",
            problem_url=f"https://{problem_host}/{slug}",
            approach=approach,
            language=language,
            difficulty=problem_metadata.difficulty,
            categories=problem_metadata.categories,
        )


def find_metadata(file_path: str) -> CommitMetadata | None:
    raw = run_git(
        "log",
        "-1",
        "--pretty=format:%at%x00%B%x00%H",
        "--follow",
        "--grep=^solution",
        "--",
        file_path,
    )
    if not raw:
        return None

    timestamp, message, sha = raw.split("\x00", maxsplit=2)
    return CommitMetadata(timestamp=int(timestamp), message=message, sha=sha)


def extract_problem_name(message: str) -> str:
    match = QUOTED_TITLE.search(message)
    if not match:
        raise RuntimeError(
            f"Could not extract problem title from commit message: {message!r}"
        )
    return match.group(1)


def slugify(problem_name: str) -> str:
    normalized = problem_name.replace(" - ", " ")
    return ILLEGAL_SYMBOLS.sub("", normalized).replace(" ", "-").lower()


def fetch_problem_metadata(slug: str, session: str | None) -> ProblemMetadata:
    if not session or not slug:
        return ProblemMetadata()

    try:
        response = requests.post(
            "https://leetcode.com/graphql",
            json={**LEETCODE_QUERY, "variables": {"titleSlug": slug}},
            headers={
                "Content-Type": "application/json",
                "Cookie": f"LEETCODE_SESSION={session}",
            },
            timeout=30,
        )
        response.raise_for_status()
        payload = response.json()
    except (requests.RequestException, ValueError):
        return ProblemMetadata()

    question = payload.get("data", {}).get("question")
    if not question:
        return ProblemMetadata()

    categories = tuple(tag["name"] for tag in question.get("topicTags", []))
    return ProblemMetadata(
        difficulty=question.get("difficulty", ""),
        categories=categories,
    )
