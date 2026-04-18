from __future__ import annotations

import pytest
from automation.commits import parse_solution_subject
from automation.errors import AutomationError


def test_parse_solution_subject() -> None:
    parsed = parse_solution_subject("solution(leetcode): add iterative 'Binary Search'")

    assert parsed.action == "add"
    assert parsed.approach == "iterative"
    assert parsed.slug == "binary-search"


def test_parse_solution_subject_rejects_invalid_format() -> None:
    with pytest.raises(AutomationError):
        parse_solution_subject("solution: Binary Search")
