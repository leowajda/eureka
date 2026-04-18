from __future__ import annotations

import re

from automation.commits import parse_solution_subject
from automation.errors import AutomationError
from automation.git import commit_subjects

CONVENTIONAL_COMMIT = re.compile(r"^[a-z]+(?:\([a-z0-9-]+\))?!?: .+$")


def validate_commit_range(*, base_revision: str, head_revision: str) -> None:
    subjects = commit_subjects(
        base_revision=base_revision,
        head_revision=head_revision,
    )
    for subject in subjects:
        validate_commit_subject(subject)


def validate_commit_subject(subject: str) -> None:
    normalized = subject.strip()
    if normalized.startswith("solution("):
        parse_solution_subject(normalized)
        return
    if not CONVENTIONAL_COMMIT.match(normalized):
        raise AutomationError(
            f"Commit '{normalized}' does not follow Conventional Commits."
        )
