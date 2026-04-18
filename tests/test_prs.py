from __future__ import annotations

import json
from pathlib import Path

import pytest
from automation.errors import AutomationError
from automation.leetcode import PullRequestProblemMetadata, RelatedProblemMetadata
from automation.prs import (
    PullRequestCommentPlan,
    PullRequestPlan,
    collect_pull_request_labels,
    render_pull_request_body,
    render_pull_request_comment,
    render_pull_request_title,
    resolve_base_branch_revision,
    resolve_primary_action,
    write_pull_request_comment_plan,
    write_pull_request_plan,
)
from automation.solution_branches import (
    ACTION_ADD,
    ACTION_REMOVE,
    ACTION_UPDATE,
    SolutionBranchChange,
)


def test_render_pull_request_title() -> None:
    title = render_pull_request_title(
        metadata=_metadata(),
        action=ACTION_ADD,
        action_labels=_action_labels(),
    )

    assert title == "Add Two Sum"


def test_render_pull_request_title_requires_action_label() -> None:
    with pytest.raises(AutomationError):
        render_pull_request_title(
            metadata=_metadata(),
            action=ACTION_ADD,
            action_labels={"update": "Update"},
        )


def test_render_pull_request_body() -> None:
    body = render_pull_request_body(_metadata())

    assert body.startswith("[Two Sum](https://leetcode.com/problems/two-sum)\n")
    assert "Related:" in body
    assert "[#167 Two Sum II - Input Array Is Sorted]" in body


def test_render_pull_request_comment() -> None:
    body = render_pull_request_comment(
        metadata=_metadata(),
        changes=(
            SolutionBranchChange(
                action=ACTION_ADD,
                language="python",
                approach="iterative",
                file_path="python/src/array/iterative/two_sum.py",
            ),
            SolutionBranchChange(
                action=ACTION_UPDATE,
                language="java",
                approach="iterative",
                file_path="java/src/main/java/array/iterative/TwoSum.java",
            ),
        ),
        action_labels=_action_labels(),
    )

    assert body.startswith("Updated [Two Sum](https://leetcode.com/problems/two-sum)\n")
    assert "- Add `python/iterative`" in body
    assert "- Update `java/iterative`" in body


def test_collect_pull_request_labels() -> None:
    labels = collect_pull_request_labels(_metadata())

    assert labels == (
        "difficulty:easy",
        "topic:array",
        "topic:hash-table",
    )


def test_resolve_primary_action_prefers_add() -> None:
    action = resolve_primary_action(
        (
            SolutionBranchChange(
                action=ACTION_ADD,
                language="python",
                approach="iterative",
                file_path="python/src/array/iterative/two_sum.py",
            ),
            SolutionBranchChange(
                action=ACTION_UPDATE,
                language="java",
                approach="iterative",
                file_path="java/src/main/java/array/iterative/TwoSum.java",
            ),
        )
    )

    assert action == ACTION_ADD


def test_resolve_primary_action_prefers_update_over_remove() -> None:
    action = resolve_primary_action(
        (
            SolutionBranchChange(
                action=ACTION_UPDATE,
                language="python",
                approach="iterative",
                file_path="python/src/array/iterative/two_sum.py",
            ),
            SolutionBranchChange(
                action=ACTION_REMOVE,
                language="java",
                approach="iterative",
                file_path="java/src/main/java/array/iterative/TwoSum.java",
            ),
        )
    )

    assert action == ACTION_UPDATE


def test_write_pull_request_plan(tmp_path: Path) -> None:
    plan = PullRequestPlan(
        title="Add Two Sum",
        body="[Two Sum](https://leetcode.com/problems/two-sum)\n",
        labels=("difficulty:easy", "topic:array"),
        head_branch="solution/two-sum",
        base_branch="master",
    )

    write_pull_request_plan(tmp_path, plan)

    payload = json.loads((tmp_path / "pull_request.json").read_text(encoding="utf-8"))
    labels = json.loads((tmp_path / "labels.json").read_text(encoding="utf-8"))

    assert payload["title"] == plan.title
    assert labels["labels"] == ["difficulty:easy", "topic:array"]


def test_write_pull_request_comment_plan(tmp_path: Path) -> None:
    plan = PullRequestCommentPlan(body="Updated [Two Sum](https://leetcode.com/problems/two-sum)\n")

    write_pull_request_comment_plan(tmp_path, plan)

    payload = json.loads((tmp_path / "comment.json").read_text(encoding="utf-8"))

    assert payload == {"body": plan.body}


def test_resolve_base_branch_revision_falls_back_to_origin(monkeypatch) -> None:
    calls: list[str] = []

    def fake_run_git(*args: str) -> str:
        calls.append(args[-1])
        if args[-1] == "origin/master":
            return "deadbeef"
        raise AutomationError("missing ref")

    monkeypatch.setattr("automation.prs.run_git", fake_run_git)

    assert resolve_base_branch_revision("master") == "deadbeef"
    assert calls == ["master", "origin/master"]


def _metadata() -> PullRequestProblemMetadata:
    return PullRequestProblemMetadata(
        slug="two-sum",
        frontend_id="1",
        name="Two Sum",
        difficulty="Easy",
        categories=("Array", "Hash Table"),
        related=(
            RelatedProblemMetadata(
                slug="two-sum-ii-input-array-is-sorted",
                frontend_id="167",
                name="Two Sum II - Input Array Is Sorted",
            ),
        ),
    )


def _action_labels() -> dict[str, str]:
    return {
        "add": "Add",
        "update": "Update",
        "remove": "Remove",
    }
