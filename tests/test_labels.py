from __future__ import annotations

import pytest
from automation.errors import AutomationError
from automation.labels import build_problem_label_names


def test_build_problem_label_names_normalizes_categories() -> None:
    labels = build_problem_label_names(
        difficulty="Easy",
        categories=("Array", "Binary Search", "Heap (Priority Queue)"),
    )

    assert labels == (
        "difficulty:easy",
        "topic:array",
        "topic:binary-search",
        "topic:heap-priority-queue",
    )


def test_build_problem_label_names_rejects_unknown_difficulty() -> None:
    with pytest.raises(AutomationError):
        build_problem_label_names(
            difficulty="Impossible",
            categories=("Array",),
        )


def test_build_problem_label_names_deduplicates_categories() -> None:
    labels = build_problem_label_names(
        difficulty="Medium",
        categories=("Array", "Array", "Binary Search"),
    )

    assert labels == (
        "difficulty:medium",
        "topic:array",
        "topic:binary-search",
    )
