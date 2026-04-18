from __future__ import annotations

import json
from collections.abc import Mapping
from dataclasses import dataclass
from pathlib import Path

from automation.config import load_solution_action_labels, load_targets
from automation.errors import AutomationError
from automation.git import merge_base, resolve_base_revision, run_git
from automation.labels import build_problem_label_names
from automation.leetcode import (
    PullRequestProblemMetadata,
    fetch_pull_request_metadata_map,
)
from automation.paths import DEFAULT_SOLUTION_ACTION_LABELS_PATH, DEFAULT_TARGETS_PATH
from automation.solution_branches import (
    ACTION_ADD,
    ACTION_REMOVE,
    ACTION_UPDATE,
    SolutionBranchChange,
    collect_solution_branch_changes,
    parse_solution_branch_name,
)


@dataclass(frozen=True)
class PullRequestPlan:
    title: str
    body: str
    labels: tuple[str, ...]
    head_branch: str
    base_branch: str


@dataclass(frozen=True)
class PullRequestCommentPlan:
    body: str


def create_pull_request_plan(
    *,
    targets_path: Path,
    action_labels_path: Path,
    base_branch: str,
    head_branch: str,
    head_revision: str,
    session_token: str | None,
    metadata_loader=fetch_pull_request_metadata_map,
) -> PullRequestPlan:
    targets = load_targets(targets_path)
    action_labels = load_solution_action_labels(action_labels_path)
    base_revision = merge_base(
        base_revision=resolve_base_branch_revision(base_branch),
        head_revision=head_revision,
    )
    changes = collect_solution_branch_changes(
        targets=targets,
        branch_name=head_branch,
        base_revision=base_revision,
        head_revision=head_revision,
    )
    if not changes:
        raise AutomationError(
            f"No solution changes detected between '{base_branch}' and '{head_revision}'."
        )

    metadata = _load_pull_request_metadata(
        slug=_branch_slug(head_branch),
        session_token=session_token,
        metadata_loader=metadata_loader,
    )
    return PullRequestPlan(
        title=render_pull_request_title(
            metadata=metadata,
            action=resolve_primary_action(changes),
            action_labels=action_labels,
        ),
        body=render_pull_request_body(metadata),
        labels=collect_pull_request_labels(metadata),
        head_branch=head_branch,
        base_branch=base_branch,
    )


def create_pull_request_comment_plan(
    *,
    targets_path: Path,
    action_labels_path: Path,
    head_branch: str,
    base_revision: str,
    head_revision: str,
    session_token: str | None,
    metadata_loader=fetch_pull_request_metadata_map,
) -> PullRequestCommentPlan | None:
    targets = load_targets(targets_path)
    action_labels = load_solution_action_labels(action_labels_path)
    resolved_base_revision = resolve_base_revision(
        base_revision=base_revision,
        head_revision=head_revision,
    )
    changes = collect_solution_branch_changes(
        targets=targets,
        branch_name=head_branch,
        base_revision=resolved_base_revision,
        head_revision=head_revision,
    )
    if not changes:
        return None

    metadata = _load_pull_request_metadata(
        slug=_branch_slug(head_branch),
        session_token=session_token,
        metadata_loader=metadata_loader,
    )
    return PullRequestCommentPlan(
        body=render_pull_request_comment(
            metadata=metadata,
            changes=changes,
            action_labels=action_labels,
        )
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


def write_pull_request_comment_plan(output_dir: Path, plan: PullRequestCommentPlan) -> None:
    output_dir.mkdir(parents=True, exist_ok=True)
    (output_dir / "comment.json").write_text(
        json.dumps({"body": plan.body}, indent=2) + "\n",
        encoding="utf-8",
    )


def render_pull_request_title(
    *,
    metadata: PullRequestProblemMetadata,
    action: str,
    action_labels: Mapping[str, str],
) -> str:
    try:
        display_action = action_labels[action]
    except KeyError as error:
        raise AutomationError(
            f"Missing pull request title label for solution action '{action}'."
        ) from error
    return f"{display_action} {metadata.name}"


def render_pull_request_body(metadata: PullRequestProblemMetadata) -> str:
    lines = [f"[{metadata.name}]({metadata.url})"]
    if metadata.related:
        lines.extend(
            [
                "",
                "Related:",
                *(
                    f"- [#{related.frontend_id} {related.name}]({related.url})"
                    for related in metadata.related
                ),
            ]
        )
    return "\n".join(lines) + "\n"


def render_pull_request_comment(
    *,
    metadata: PullRequestProblemMetadata,
    changes: tuple[SolutionBranchChange, ...],
    action_labels: Mapping[str, str],
) -> str:
    lines = [
        f"Updated [{metadata.name}]({metadata.url})",
        "",
        "Changes in this push:",
    ]
    for change in changes:
        try:
            display_action = action_labels[change.action]
        except KeyError as error:
            raise AutomationError(
                f"Missing pull request title label for solution action '{change.action}'."
            ) from error
        lines.append(f"- {display_action} `{change.implementation}`")
    return "\n".join(lines) + "\n"


def collect_pull_request_labels(metadata: PullRequestProblemMetadata) -> tuple[str, ...]:
    return build_problem_label_names(
        difficulty=metadata.difficulty,
        categories=metadata.categories,
    )


def resolve_primary_action(changes: tuple[SolutionBranchChange, ...]) -> str:
    actions = {change.action for change in changes}
    if actions == {ACTION_ADD}:
        return ACTION_ADD
    if ACTION_ADD in actions:
        return ACTION_ADD
    if ACTION_UPDATE in actions:
        return ACTION_UPDATE
    return ACTION_REMOVE


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
    action_labels_path: Path = DEFAULT_SOLUTION_ACTION_LABELS_PATH,
    base_branch: str,
    head_branch: str,
    head_revision: str,
    session_token: str | None,
    output_dir: Path,
) -> PullRequestPlan:
    plan = create_pull_request_plan(
        targets_path=targets_path,
        action_labels_path=action_labels_path,
        base_branch=base_branch,
        head_branch=head_branch,
        head_revision=head_revision,
        session_token=session_token,
    )
    write_pull_request_plan(output_dir, plan)
    return plan


def create_and_write_pull_request_comment_plan(
    *,
    targets_path: Path = DEFAULT_TARGETS_PATH,
    action_labels_path: Path = DEFAULT_SOLUTION_ACTION_LABELS_PATH,
    head_branch: str,
    base_revision: str,
    head_revision: str,
    session_token: str | None,
    output_dir: Path,
) -> PullRequestCommentPlan | None:
    plan = create_pull_request_comment_plan(
        targets_path=targets_path,
        action_labels_path=action_labels_path,
        head_branch=head_branch,
        base_revision=base_revision,
        head_revision=head_revision,
        session_token=session_token,
    )
    if plan is None:
        return None
    write_pull_request_comment_plan(output_dir, plan)
    return plan


def _branch_slug(head_branch: str) -> str:
    return parse_solution_branch_name(head_branch)


def _load_pull_request_metadata(
    *,
    slug: str,
    session_token: str | None,
    metadata_loader,
) -> PullRequestProblemMetadata:
    metadata_map = metadata_loader({slug}, session_token)
    try:
        return metadata_map[slug]
    except KeyError as error:
        raise AutomationError(f"Missing pull request metadata for slug '{slug}'.") from error
