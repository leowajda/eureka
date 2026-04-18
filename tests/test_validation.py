from __future__ import annotations

import pytest
from automation.errors import AutomationError
from automation.validation import validate_commit_subject


def test_validate_commit_subject_accepts_solution_commit() -> None:
    validate_commit_subject("solution(leetcode): add iterative 'Binary Search'")


def test_validate_commit_subject_accepts_remove_solution_commit() -> None:
    validate_commit_subject("solution(leetcode): remove iterative 'Binary Search'")


def test_validate_commit_subject_accepts_conventional_commit() -> None:
    validate_commit_subject("ci(catalog): sync generated problem catalog")


def test_validate_commit_subject_rejects_invalid_commit() -> None:
    with pytest.raises(AutomationError):
        validate_commit_subject("bad commit")
