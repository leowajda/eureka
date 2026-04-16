from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass
from enum import StrEnum
from pathlib import Path

from automation.catalog import (
    build_generated_catalog,
    collect_solution_records,
    collect_solution_records_for_files,
    load_generated_catalog_if_present,
    write_generated_catalog,
)
from automation.config import load_targets
from automation.errors import AutomationError
from automation.git import diff_files, resolve_base_revision
from automation.leetcode import fetch_problem_metadata_map
from automation.models import (
    CatalogProblem,
    GeneratedCatalog,
    LanguageTarget,
    ProblemImplementation,
    ProblemMetadata,
    SolutionCommit,
)


class ChangeAction(StrEnum):
    REMOVE = "remove"
    UPDATE = "update"
    ADD = "add"


@dataclass(frozen=True)
class SolutionChange:
    action: ChangeAction
    solution: SolutionCommit


def sync_catalog(
    *,
    targets_path: Path,
    catalog_path: Path,
    source_url_base: str,
    base_revision: str | None,
    head_revision: str,
    session_token: str | None,
) -> None:
    targets = load_targets(targets_path)
    current_catalog = load_generated_catalog_if_present(catalog_path)
    changes = collect_incremental_changes(
        targets=targets,
        source_url_base=source_url_base,
        base_revision=resolve_base_revision(
            base_revision=base_revision,
            head_revision=head_revision,
        ),
        head_revision=head_revision,
    )
    generated_catalog = merge_incremental_catalog(
        current_catalog=current_catalog,
        targets=targets,
        session_token=session_token,
        changes=changes,
    )
    write_generated_catalog(catalog_path, generated_catalog)


def replay_catalog(
    *,
    targets_path: Path,
    catalog_path: Path,
    source_url_base: str,
    session_token: str | None,
) -> None:
    targets = load_targets(targets_path)
    solutions = collect_solution_records(
        targets=targets,
        source_url_base=source_url_base,
    )
    metadata_catalog = fetch_problem_metadata_map(
        slugs={solution.slug for solution in solutions},
        session_token=session_token,
    )
    generated_catalog = build_generated_catalog(
        targets=targets,
        metadata_catalog=metadata_catalog,
        solutions=solutions,
    )
    write_generated_catalog(catalog_path, generated_catalog)


def collect_incremental_changes(
    *,
    targets: tuple[LanguageTarget, ...],
    source_url_base: str,
    base_revision: str,
    head_revision: str,
) -> tuple[SolutionChange, ...]:
    changes: list[SolutionChange] = []

    for target in targets:
        changes.extend(
            _collect_changes_for_target(
                target=target,
                source_url_base=source_url_base,
                base_revision=base_revision,
                head_revision=head_revision,
            )
        )

    return tuple(changes)


def merge_incremental_catalog(
    *,
    current_catalog: GeneratedCatalog,
    targets: tuple[LanguageTarget, ...],
    session_token: str | None,
    changes: tuple[SolutionChange, ...],
    metadata_loader: Callable[[set[str], str | None], dict[str, ProblemMetadata]] = fetch_problem_metadata_map,
) -> GeneratedCatalog:
    problems = {problem.slug: problem for problem in current_catalog.problems}

    for change in changes:
        if change.action in {ChangeAction.REMOVE, ChangeAction.UPDATE}:
            _remove_implementation(problems, change.solution.source_url)

    metadata_catalog = {
        problem.slug: ProblemMetadata.from_problem(problem)
        for problem in problems.values()
    }
    missing_slugs = {
        change.solution.slug
        for change in changes
        if change.action in {ChangeAction.ADD, ChangeAction.UPDATE}
        and change.solution.slug not in metadata_catalog
    }
    if missing_slugs:
        metadata_catalog.update(metadata_loader(missing_slugs, session_token))

    for change in changes:
        if change.action is ChangeAction.REMOVE:
            continue

        metadata = metadata_catalog.get(change.solution.slug)
        if metadata is None:
            raise AutomationError(f"Missing metadata for slug '{change.solution.slug}'.")

        problem = problems.get(change.solution.slug, CatalogProblem.from_metadata(metadata))
        problems[change.solution.slug] = problem.with_implementation(
            ProblemImplementation(
                language=change.solution.language,
                approach=change.solution.approach,
                source_url=change.solution.source_url,
            )
        )

    return GeneratedCatalog(
        languages=tuple(target.catalog_language() for target in targets),
        problems=tuple(problem for _, problem in sorted(problems.items(), key=lambda item: item[0])),
    )


def _collect_changes_for_target(
    *,
    target: LanguageTarget,
    source_url_base: str,
    base_revision: str,
    head_revision: str,
) -> tuple[SolutionChange, ...]:
    changes: list[SolutionChange] = []
    for action, diff_filter in (
        (ChangeAction.REMOVE, "D"),
        (ChangeAction.UPDATE, "M"),
        (ChangeAction.ADD, "A"),
    ):
        file_paths = diff_files(
            base_revision=base_revision,
            head_revision=head_revision,
            path_prefix=target.path_prefix,
            diff_filter=diff_filter,
        )
        changes.extend(
            SolutionChange(action=action, solution=solution)
            for solution in collect_solution_records_for_files(
                file_paths=file_paths,
                target=target,
                source_url_base=source_url_base,
            )
        )

    return tuple(changes)


def _remove_implementation(problems: dict[str, CatalogProblem], source_url: str) -> None:
    for slug, problem in tuple(problems.items()):
        updated = problem.without_source_url(source_url)
        if updated is problem:
            continue
        if updated is None:
            del problems[slug]
            return
        problems[slug] = updated
        return
