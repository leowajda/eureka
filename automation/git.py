from __future__ import annotations

import subprocess
from pathlib import Path

from automation.errors import AutomationError
from automation.utils import normalize_path

ZERO_SHA = "0" * 40


def run_git(*args: str, cwd: Path | None = None) -> str:
    try:
        completed = subprocess.run(
            ["git", *args],
            check=True,
            cwd=cwd,
            capture_output=True,
            text=True,
        )
    except subprocess.CalledProcessError as error:
        stderr = error.stderr.strip()
        raise AutomationError(stderr or str(error)) from error
    return completed.stdout.strip()


def tracked_files(path_prefix: str | None = None) -> tuple[str, ...]:
    command = ["ls-files"]
    if path_prefix:
        command.extend(["--", path_prefix])
    output = run_git(*command)
    if not output:
        return ()
    return tuple(normalize_path(line) for line in output.splitlines() if line.strip())


def diff_files(
    *,
    base_revision: str,
    head_revision: str,
    path_prefix: str,
    diff_filter: str,
) -> tuple[str, ...]:
    output = run_git(
        "diff",
        "--no-renames",
        f"--diff-filter={diff_filter}",
        "--name-only",
        base_revision,
        head_revision,
        "--",
        normalize_path(path_prefix),
    )
    if not output:
        return ()
    return tuple(normalize_path(line) for line in output.splitlines() if line.strip())


def merge_base(*, base_revision: str, head_revision: str) -> str:
    return run_git("merge-base", base_revision, head_revision)


def resolve_base_revision(*, base_revision: str | None, head_revision: str) -> str:
    if base_revision and base_revision != ZERO_SHA:
        return base_revision
    if _revision_exists(f"{head_revision}^"):
        return run_git("rev-parse", f"{head_revision}^")
    return run_git("hash-object", "-t", "tree", "/dev/null")


def commit_subjects(*, base_revision: str, head_revision: str) -> tuple[str, ...]:
    output = run_git(
        "log",
        "--format=%s",
        "--no-merges",
        f"{base_revision}..{head_revision}",
    )
    if not output:
        return ()
    return tuple(subject.strip() for subject in output.splitlines() if subject.strip())


def latest_solution_subject(file_path: str) -> str | None:
    output = run_git(
        "log",
        "--follow",
        "--pretty=format:%s",
        "--",
        normalize_path(file_path),
    )
    if not output:
        return None

    for subject in output.splitlines():
        if subject.startswith("solution("):
            return subject.strip()
    return None


def _revision_exists(revision: str) -> bool:
    completed = subprocess.run(
        ["git", "rev-parse", "--verify", revision],
        cwd=None,
        capture_output=True,
        text=True,
        check=False,
    )
    return completed.returncode == 0
