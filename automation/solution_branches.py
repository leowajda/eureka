from __future__ import annotations

import re
from dataclasses import dataclass

from automation.catalog import collect_solution_records_for_files
from automation.commits import parse_solution_subject
from automation.errors import AutomationError
from automation.git import commit_subjects, diff_files
from automation.models import LanguageTarget
from automation.utils import extract_approach, is_solution_candidate_path, normalize_path

ACTION_ADD = "add"
ACTION_UPDATE = "update"
ACTION_REMOVE = "remove"
SOLUTION_BRANCH = re.compile(r"^solution/(?P<slug>[a-z0-9]+(?:-[a-z0-9]+)*)$")
DIFF_ACTIONS = (
    (ACTION_ADD, "A"),
    (ACTION_UPDATE, "M"),
    (ACTION_REMOVE, "D"),
)


@dataclass(frozen=True)
class SolutionBranchChange:
    action: str
    language: str
    approach: str
    file_path: str

    @property
    def implementation(self) -> str:
        return f"{self.language}/{self.approach}"


def parse_solution_branch_name(branch_name: str) -> str:
    match = SOLUTION_BRANCH.fullmatch(branch_name.strip())
    if match is None:
        raise AutomationError(
            f"Solution automation requires branches to match 'solution/<slug>', got '{branch_name}'."
        )
    return match.group("slug")


def validate_solution_branch_subjects(
    *,
    branch_name: str,
    base_revision: str,
    head_revision: str,
) -> str:
    expected_slug = parse_solution_branch_name(branch_name)
    for subject in commit_subjects(base_revision=base_revision, head_revision=head_revision):
        normalized = subject.strip()
        if not normalized.startswith("solution("):
            continue
        parsed = parse_solution_subject(normalized)
        if parsed.slug != expected_slug:
            raise AutomationError(
                f"Solution branch '{branch_name}' can only contain problem slug '{expected_slug}', "
                f"but commit '{normalized}' resolves to '{parsed.slug}'."
            )
    return expected_slug


def collect_solution_branch_changes(
    *,
    targets: tuple[LanguageTarget, ...],
    branch_name: str,
    base_revision: str,
    head_revision: str,
) -> tuple[SolutionBranchChange, ...]:
    expected_slug = validate_solution_branch_subjects(
        branch_name=branch_name,
        base_revision=base_revision,
        head_revision=head_revision,
    )
    changes: list[SolutionBranchChange] = []

    for target in targets:
        for action, diff_filter in DIFF_ACTIONS:
            file_paths = diff_files(
                base_revision=base_revision,
                head_revision=head_revision,
                path_prefix=target.path_prefix,
                diff_filter=diff_filter,
            )
            if action == ACTION_REMOVE:
                changes.extend(
                    _collect_deleted_solution_branch_changes(
                        target=target,
                        file_paths=file_paths,
                    )
                )
                continue

            for solution in collect_solution_records_for_files(
                file_paths=file_paths,
                target=target,
            ):
                if solution.slug != expected_slug:
                    raise AutomationError(
                        f"Solution branch '{branch_name}' can only contain problem slug "
                        f"'{expected_slug}', but file '{solution.file_path}' resolves to "
                        f"'{solution.slug}'."
                    )
                changes.append(
                    SolutionBranchChange(
                        action=action,
                        language=solution.language,
                        approach=solution.approach,
                        file_path=solution.file_path,
                    )
                )

    return tuple(
        sorted(
            changes,
            key=lambda change: (
                _action_sort_key(change.action),
                change.language,
                change.approach,
                change.file_path,
            ),
        )
    )


def _collect_deleted_solution_branch_changes(
    *,
    target: LanguageTarget,
    file_paths: tuple[str, ...],
) -> tuple[SolutionBranchChange, ...]:
    changes: list[SolutionBranchChange] = []
    for file_path in file_paths:
        normalized_path = normalize_path(file_path)
        if not target.matches(normalized_path) or not is_solution_candidate_path(normalized_path):
            continue

        approach = extract_approach(normalized_path)
        if approach is None:
            continue

        changes.append(
            SolutionBranchChange(
                action=ACTION_REMOVE,
                language=target.language,
                approach=approach,
                file_path=normalized_path,
            )
        )

    return tuple(changes)


def _action_sort_key(action: str) -> int:
    order = {
        ACTION_ADD: 0,
        ACTION_UPDATE: 1,
        ACTION_REMOVE: 2,
    }
    return order.get(action, len(order))
