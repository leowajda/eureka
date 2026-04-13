from __future__ import annotations

from dataclasses import dataclass
from pathlib import PurePosixPath
import re
from typing import Self

from action import Action
from leetcode import fetch_problem_metadata
from workflow_support import LanguageTarget, run_git

QUOTED_TITLE = re.compile(r"'([^']+)'")
ILLEGAL_SYMBOLS = re.compile(r"[^a-zA-Z0-9- ]")
APPROACHES = {"iterative", "recursive"}


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
    difficulty: str
    categories: tuple[str, ...]

    @classmethod
    def from_file(
        cls,
        file_path: str,
        action: Action,
        *,
        target: LanguageTarget,
        leetcode_session: str | None,
    ) -> Self | None:
        metadata = _load_commit_metadata(file_path)
        if metadata is None:
            return None

        timestamp, message, sha = metadata
        problem_name = _extract_problem_name(message)
        slug = _slugify(problem_name)
        difficulty, categories = fetch_problem_metadata(slug, leetcode_session)
        return cls(
            file_path=file_path,
            action=action,
            timestamp=timestamp,
            sha=sha,
            problem_name=problem_name,
            slug=slug,
            source_url=target.source_url(file_path),
            problem_url=f"https://{_problem_host(message)}/{slug}",
            approach=_extract_approach(file_path),
            language=target.language,
            difficulty=difficulty,
            categories=tuple(categories),
        )


def _load_commit_metadata(file_path: str) -> tuple[int, str, str] | None:
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
    return int(timestamp), message, sha


def _extract_problem_name(message: str) -> str:
    match = QUOTED_TITLE.search(message)
    if match:
        return match.group(1)
    raise RuntimeError(
        f"Could not extract problem title from commit message: {message!r}"
    )


def _slugify(problem_name: str) -> str:
    normalized = problem_name.replace(" - ", " ")
    return ILLEGAL_SYMBOLS.sub("", normalized).replace(" ", "-").lower()


def _problem_host(message: str) -> str:
    return (
        "leetcode.com/problems"
        if "leetcode" in message.lower()
        else "hackerrank.com/challenges"
    )


def _extract_approach(file_path: str) -> str:
    for segment in PurePosixPath(file_path).parts:
        if segment in APPROACHES:
            return segment
    raise RuntimeError(f"Could not infer approach from file path: {file_path!r}")
