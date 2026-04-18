from __future__ import annotations

import json
from pathlib import Path

from automation.errors import AutomationError
from automation.leetcode import PullRequestProblemMetadata, RelatedProblemMetadata
from automation.models import LanguageTarget
from automation.prs import (
    PullRequestPlan,
    PullRequestProblem,
    PullRequestSolution,
    build_pull_request_problems,
    collect_pull_request_labels,
    render_pull_request_body,
    render_pull_request_title,
    resolve_base_branch_revision,
    write_pull_request_plan,
)


def test_render_pull_request_title_for_single_problem() -> None:
    title = render_pull_request_title(
        (
            _problem(
                slug="two-sum",
                name="Two Sum",
                frontend_id="1",
                implementations=("python/iterative",),
                language_labels=("Python",),
                actions=("add",),
            ),
        )
    )

    assert title == "add Two Sum in Python"


def test_render_pull_request_title_for_multiple_problems() -> None:
    title = render_pull_request_title(
        (
            _problem(slug="two-sum", name="Two Sum", frontend_id="1"),
            _problem(slug="binary-search", name="Binary Search", frontend_id="704"),
        )
    )

    assert title == "Multiple LeetCode solutions"


def test_render_pull_request_body() -> None:
    body = render_pull_request_body(
        (
            _problem(
                slug="binary-search",
                name="Binary Search",
                frontend_id="704",
                implementations=("java/iterative", "python/iterative"),
                related=(
                    RelatedProblemMetadata(
                        slug="search-insert-position",
                        frontend_id="35",
                        name="Search Insert Position",
                    ),
                ),
            ),
        )
    )

    assert "[#704 Binary Search](https://leetcode.com/problems/binary-search)" in body
    assert "`java/iterative`, `python/iterative`" in body
    assert "Related:" in body


def test_collect_pull_request_labels() -> None:
    labels = collect_pull_request_labels(
        (
            _problem(
                slug="binary-search",
                name="Binary Search",
                frontend_id="704",
                difficulty="Easy",
                categories=("Array", "Binary Search"),
            ),
        )
    )

    assert labels == (
        "difficulty:easy",
        "topic:array",
        "topic:binary-search",
    )


def test_build_pull_request_problems_groups_solutions() -> None:
    targets = (
        LanguageTarget(
            language="java",
            label="Java",
            code_language="java",
            path_prefix="java",
            path_glob="java/src/main/**/*.java",
        ),
        LanguageTarget(
            language="python",
            label="Python",
            code_language="python",
            path_prefix="python",
            path_glob="python/src/**/*.py",
        ),
    )
    solutions = (
        PullRequestSolution(
            slug="binary-search",
            action="add",
            language="java",
            language_label="Java",
            approach="iterative",
        ),
        PullRequestSolution(
            slug="binary-search",
            action="add",
            language="python",
            language_label="Python",
            approach="iterative",
        ),
    )
    metadata_map = {
        "binary-search": PullRequestProblemMetadata(
            slug="binary-search",
            frontend_id="704",
            name="Binary Search",
            difficulty="Easy",
            categories=("Array", "Binary Search"),
        )
    }

    problems = build_pull_request_problems(
        targets=targets,
        solutions=solutions,
        metadata_map=metadata_map,
    )

    assert problems[0].implementations == ("java/iterative", "python/iterative")
    assert problems[0].language_labels == ("Java", "Python")


def test_write_pull_request_plan(tmp_path: Path) -> None:
    plan = PullRequestPlan(
        title="add Two Sum in Python",
        body="1. [#1 Two Sum](https://leetcode.com/problems/two-sum)\n",
        labels=("difficulty:easy", "topic:array"),
        head_branch="solution/two-sum",
        base_branch="master",
    )

    write_pull_request_plan(tmp_path, plan)

    payload = json.loads((tmp_path / "pull_request.json").read_text(encoding="utf-8"))
    labels = json.loads((tmp_path / "labels.json").read_text(encoding="utf-8"))

    assert payload["title"] == plan.title
    assert labels["labels"] == ["difficulty:easy", "topic:array"]


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


def _problem(
    *,
    slug: str,
    name: str,
    frontend_id: str,
    implementations: tuple[str, ...] = ("python/iterative",),
    difficulty: str = "Easy",
    categories: tuple[str, ...] = ("Array",),
    language_labels: tuple[str, ...] = ("Python",),
    actions: tuple[str, ...] = ("add",),
    related: tuple[RelatedProblemMetadata, ...] = (),
) -> PullRequestProblem:
    return PullRequestProblem(
        slug=slug,
        name=name,
        frontend_id=frontend_id,
        url=f"https://leetcode.com/problems/{slug}",
        difficulty=difficulty,
        categories=categories,
        implementations=implementations,
        language_labels=language_labels,
        actions=actions,
        related=related,
    )
