from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path

from automation.catalog import collect_solution_records_for_files
from automation.commits import parse_solution_subject
from automation.config import load_targets
from automation.errors import AutomationError
from automation.git import diff_files, latest_solution_subject, merge_base, run_git
from automation.labels import build_problem_label_names
from automation.leetcode import (
    PullRequestProblemMetadata,
    RelatedProblemMetadata,
    fetch_pull_request_metadata_map,
)
from automation.models import LanguageTarget
from automation.paths import DEFAULT_TARGETS_PATH

MAX_RELATED_PROBLEMS = 3


@dataclass(frozen=True)
class PullRequestSolution:
    slug: str
    action: str
    language: str
    language_label: str
    approach: str


@dataclass(frozen=True)
class PullRequestProblem:
    slug: str
    name: str
    frontend_id: str
    url: str
    difficulty: str
    categories: tuple[str, ...]
    implementations: tuple[str, ...]
    language_labels: tuple[str, ...]
    actions: tuple[str, ...]
    related: tuple[RelatedProblemMetadata, ...]


@dataclass(frozen=True)
class PullRequestPlan:
    title: str
    body: str
    labels: tuple[str, ...]
    head_branch: str
    base_branch: str


def create_pull_request_plan(
    *,
    targets_path: Path,
    base_branch: str,
    head_branch: str,
    head_revision: str,
    session_token: str | None,
    metadata_loader=fetch_pull_request_metadata_map,
) -> PullRequestPlan:
    targets = load_targets(targets_path)
    solutions = collect_pull_request_solutions(
        targets=targets,
        base_branch=base_branch,
        head_revision=head_revision,
    )
    metadata_map = metadata_loader(
        {solution.slug for solution in solutions},
        session_token,
    )
    problems = build_pull_request_problems(
        targets=targets,
        solutions=solutions,
        metadata_map=metadata_map,
    )
    return PullRequestPlan(
        title=render_pull_request_title(problems),
        body=render_pull_request_body(problems),
        labels=collect_pull_request_labels(problems),
        head_branch=head_branch,
        base_branch=base_branch,
    )


def write_pull_request_plan(output_dir: Path, plan: PullRequestPlan) -> None:
    output_dir.mkdir(parents=True, exist_ok=True)
    pull_request_payload = {
        "title": plan.title,
        "body": plan.body,
        "head": plan.head_branch,
        "base": plan.base_branch,
    }
    label_payload = {"labels": list(plan.labels)}

    (output_dir / "pull_request.json").write_text(
        json.dumps(pull_request_payload, indent=2) + "\n",
        encoding="utf-8",
    )
    (output_dir / "labels.json").write_text(
        json.dumps(label_payload, indent=2) + "\n",
        encoding="utf-8",
    )


def collect_pull_request_solutions(
    *,
    targets: tuple[LanguageTarget, ...],
    base_branch: str,
    head_revision: str,
) -> tuple[PullRequestSolution, ...]:
    base_revision = merge_base(
        base_revision=resolve_base_branch_revision(base_branch),
        head_revision=head_revision,
    )
    solutions: list[PullRequestSolution] = []

    for target in targets:
        file_paths = (
            *diff_files(
                base_revision=base_revision,
                head_revision=head_revision,
                path_prefix=target.path_prefix,
                diff_filter="A",
            ),
            *diff_files(
                base_revision=base_revision,
                head_revision=head_revision,
                path_prefix=target.path_prefix,
                diff_filter="M",
            ),
        )
        for solution in collect_solution_records_for_files(
            file_paths=file_paths,
            target=target,
        ):
            subject = latest_solution_subject(solution.file_path)
            if subject is None:
                raise AutomationError(
                    f"Could not resolve the latest solution commit subject for '{solution.file_path}'."
                )
            parsed = parse_solution_subject(subject)
            solutions.append(
                PullRequestSolution(
                    slug=solution.slug,
                    action=parsed.action,
                    language=solution.language,
                    language_label=target.label,
                    approach=solution.approach,
                )
            )

    if not solutions:
        raise AutomationError(
            f"No solution changes detected between '{base_branch}' and '{head_revision}'."
        )

    return tuple(
        sorted(
            solutions,
            key=lambda solution: (solution.slug, solution.language, solution.approach),
        )
    )


def build_pull_request_problems(
    *,
    targets: tuple[LanguageTarget, ...],
    solutions: tuple[PullRequestSolution, ...],
    metadata_map: dict[str, PullRequestProblemMetadata],
) -> tuple[PullRequestProblem, ...]:
    language_order = {target.language: index for index, target in enumerate(targets)}
    grouped: dict[str, list[PullRequestSolution]] = {}
    for solution in solutions:
        grouped.setdefault(solution.slug, []).append(solution)

    problems: list[PullRequestProblem] = []
    for slug, grouped_solutions in grouped.items():
        metadata = metadata_map.get(slug)
        if metadata is None:
            raise AutomationError(f"Missing pull request metadata for slug '{slug}'.")

        implementations = tuple(
            sorted(
                {f"{solution.language}/{solution.approach}" for solution in grouped_solutions},
                key=lambda implementation: (
                    language_order.get(implementation.split("/", 1)[0], len(language_order)),
                    implementation,
                ),
            )
        )
        language_labels = tuple(
            sorted(
                {solution.language_label for solution in grouped_solutions},
                key=lambda label: next(
                    (
                        language_order[target.language]
                        for target in targets
                        if target.label == label
                    ),
                    len(language_order),
                ),
            )
        )
        actions = tuple(sorted({solution.action for solution in grouped_solutions}))
        problems.append(
            PullRequestProblem(
                slug=slug,
                name=metadata.name,
                frontend_id=metadata.frontend_id,
                url=metadata.url,
                difficulty=metadata.difficulty,
                categories=metadata.categories,
                implementations=implementations,
                language_labels=language_labels,
                actions=actions,
                related=metadata.related[:MAX_RELATED_PROBLEMS],
            )
        )

    return tuple(
        sorted(
            problems,
            key=lambda problem: (_frontend_id_sort_key(problem.frontend_id), problem.name),
        )
    )


def render_pull_request_title(problems: tuple[PullRequestProblem, ...]) -> str:
    if len(problems) != 1:
        return "Multiple LeetCode solutions"

    (problem,) = problems
    action = problem.actions[0] if len(problem.actions) == 1 else "change"
    languages = ", ".join(problem.language_labels)
    return f"{action} {problem.name} in {languages}"


def render_pull_request_body(problems: tuple[PullRequestProblem, ...]) -> str:
    lines: list[str] = []

    for index, problem in enumerate(problems, start=1):
        lines.append(f"{index}. [#{problem.frontend_id} {problem.name}]({problem.url})")
        lines.append(
            "   " + ", ".join(f"`{implementation}`" for implementation in problem.implementations)
        )
        if problem.related:
            lines.append("   Related:")
            lines.extend(
                f"   - [#{related.frontend_id} {related.name}]({related.url})"
                for related in problem.related
            )
        lines.append("")

    return "\n".join(lines).rstrip() + "\n"


def collect_pull_request_labels(problems: tuple[PullRequestProblem, ...]) -> tuple[str, ...]:
    labels = {
        label
        for problem in problems
        for label in build_problem_label_names(
            difficulty=problem.difficulty,
            categories=problem.categories,
        )
    }
    return tuple(sorted(labels))


def _frontend_id_sort_key(frontend_id: str) -> tuple[int, str]:
    if frontend_id.isdigit():
        return (int(frontend_id), frontend_id)
    return (10**9, frontend_id)


def resolve_base_branch_revision(base_branch: str) -> str:
    for candidate in (base_branch, f"origin/{base_branch}"):
        try:
            return run_git("rev-parse", "--verify", candidate)
        except AutomationError:
            continue
    raise AutomationError(f"Could not resolve base branch '{base_branch}' locally.")


def create_and_write_pull_request_plan(
    *,
    targets_path: Path = DEFAULT_TARGETS_PATH,
    base_branch: str,
    head_branch: str,
    head_revision: str,
    session_token: str | None,
    output_dir: Path,
) -> PullRequestPlan:
    plan = create_pull_request_plan(
        targets_path=targets_path,
        base_branch=base_branch,
        head_branch=head_branch,
        head_revision=head_revision,
        session_token=session_token,
    )
    write_pull_request_plan(output_dir, plan)
    return plan
