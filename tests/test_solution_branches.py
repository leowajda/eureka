from __future__ import annotations

import pytest
from automation.errors import AutomationError
from automation.models import LanguageTarget
from automation.solution_branches import (
    ACTION_REMOVE,
    collect_solution_branch_changes,
    parse_solution_branch_name,
)


def test_parse_solution_branch_name() -> None:
    assert parse_solution_branch_name("solution/two-sum") == "two-sum"


def test_parse_solution_branch_name_rejects_invalid_branch() -> None:
    with pytest.raises(AutomationError):
        parse_solution_branch_name("feature/two-sum")


def test_collect_solution_branch_changes_validates_slug(monkeypatch) -> None:
    target = LanguageTarget(
        language="python",
        label="Python",
        code_language="python",
        path_prefix="python",
        path_glob="python/src/**/*.py",
    )

    monkeypatch.setattr(
        "automation.solution_branches.commit_subjects",
        lambda **_: ("solution(leetcode): add iterative 'Binary Search'",),
    )
    monkeypatch.setattr(
        "automation.solution_branches.diff_files",
        lambda **kwargs: ("python/src/array/iterative/binary_search.py",)
        if kwargs["diff_filter"] == "A"
        else (),
    )
    monkeypatch.setattr(
        "automation.solution_branches.collect_solution_records_for_files",
        lambda **_: (
            type(
                "SolutionRecord",
                (),
                {
                    "slug": "binary-search",
                    "language": "python",
                    "approach": "iterative",
                    "file_path": "python/src/array/iterative/binary_search.py",
                },
            )(),
        ),
    )

    with pytest.raises(AutomationError):
        collect_solution_branch_changes(
            targets=(target,),
            branch_name="solution/two-sum",
            base_revision="base",
            head_revision="head",
        )


def test_collect_solution_branch_changes_tracks_deleted_files(monkeypatch) -> None:
    target = LanguageTarget(
        language="python",
        label="Python",
        code_language="python",
        path_prefix="python",
        path_glob="python/src/**/*.py",
    )

    monkeypatch.setattr("automation.solution_branches.commit_subjects", lambda **_: ())
    monkeypatch.setattr(
        "automation.solution_branches.diff_files",
        lambda **kwargs: (
            ("python/src/array/iterative/two_sum.py",)
            if kwargs["diff_filter"] == "D"
            else ()
        ),
    )

    changes = collect_solution_branch_changes(
        targets=(target,),
        branch_name="solution/two-sum",
        base_revision="base",
        head_revision="head",
    )

    assert len(changes) == 1
    assert changes[0].action == ACTION_REMOVE
    assert changes[0].language == "python"
    assert changes[0].approach == "iterative"
