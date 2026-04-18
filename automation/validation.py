from __future__ import annotations

import re
from pathlib import Path

from automation.commits import parse_solution_subject
from automation.config import load_targets
from automation.errors import AutomationError
from automation.git import commit_subjects
from automation.paths import DEFAULT_TARGETS_PATH
from automation.solution_branches import collect_solution_branch_changes, parse_solution_branch_name

CONVENTIONAL_COMMIT = re.compile(r"^[a-z]+(?:\([a-z0-9-]+\))?!?: .+$")


def validate_commit_range(
    *,
    base_revision: str,
    head_revision: str,
    branch_name: str | None = None,
    targets_path: Path = DEFAULT_TARGETS_PATH,
) -> None:
    expected_solution_slug = None
    if branch_name is not None:
        try:
            expected_solution_slug = parse_solution_branch_name(branch_name)
        except AutomationError:
            expected_solution_slug = None

    subjects = commit_subjects(
        base_revision=base_revision,
        head_revision=head_revision,
    )
    for subject in subjects:
        validate_commit_subject(subject, expected_solution_slug=expected_solution_slug)

    if expected_solution_slug is None:
        return

    collect_solution_branch_changes(
        targets=load_targets(targets_path),
        branch_name=branch_name,
        base_revision=base_revision,
        head_revision=head_revision,
    )


def validate_commit_subject(subject: str, *, expected_solution_slug: str | None = None) -> None:
    normalized = subject.strip()
    if normalized.startswith("solution("):
        parsed = parse_solution_subject(normalized)
        if expected_solution_slug is not None and parsed.slug != expected_solution_slug:
            raise AutomationError(
                f"Commit '{normalized}' does not match solution branch slug '{expected_solution_slug}'."
            )
        return
    if not CONVENTIONAL_COMMIT.match(normalized):
        raise AutomationError(
            f"Commit '{normalized}' does not follow Conventional Commits."
        )
