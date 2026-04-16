from __future__ import annotations

from pathlib import Path

from automation.commits import parse_solution_subject
from automation.errors import AutomationError
from automation.git import latest_solution_subject, tracked_files
from automation.models import (
    CatalogProblem,
    GeneratedCatalog,
    LanguageTarget,
    ProblemImplementation,
    ProblemMetadata,
    SolutionCommit,
)
from automation.utils import extract_approach, is_solution_candidate_path
from automation.yamlio import dump_yaml, load_yaml


def load_generated_catalog(path: Path) -> GeneratedCatalog:
    try:
        return GeneratedCatalog.from_payload(load_yaml(path))
    except (OSError, TypeError, ValueError, KeyError) as error:
        raise AutomationError(f"Could not load generated problem catalog from '{path}': {error}") from error


def load_generated_catalog_if_present(path: Path) -> GeneratedCatalog:
    if not path.exists():
        return GeneratedCatalog.empty()
    return load_generated_catalog(path)


def write_generated_catalog(path: Path, catalog: GeneratedCatalog) -> None:
    dump_yaml(path, catalog.to_payload())


def collect_solution_records(
    *,
    targets: tuple[LanguageTarget, ...],
    source_url_base: str,
) -> tuple[SolutionCommit, ...]:
    records: list[SolutionCommit] = []

    for target in targets:
        for file_path in tracked_files(target.path_prefix):
            solution = _build_solution_record(
                file_path=file_path,
                target=target,
                source_url_base=source_url_base,
            )
            if solution is not None:
                records.append(solution)

    return tuple(
        sorted(
            records,
            key=lambda solution: (solution.slug, solution.language, solution.approach, solution.file_path),
        )
    )


def collect_solution_records_for_files(
    *,
    file_paths: tuple[str, ...],
    target: LanguageTarget,
    source_url_base: str,
) -> tuple[SolutionCommit, ...]:
    records: list[SolutionCommit] = []
    for file_path in file_paths:
        solution = _build_solution_record(
            file_path=file_path,
            target=target,
            source_url_base=source_url_base,
        )
        if solution is not None:
            records.append(solution)

    return tuple(
        sorted(
            records,
            key=lambda solution: (solution.slug, solution.language, solution.approach, solution.file_path),
        )
    )


def build_generated_catalog(
    *,
    targets: tuple[LanguageTarget, ...],
    metadata_catalog: dict[str, ProblemMetadata],
    solutions: tuple[SolutionCommit, ...],
) -> GeneratedCatalog:
    problems: dict[str, CatalogProblem] = {}

    for solution in solutions:
        metadata = metadata_catalog.get(solution.slug)
        if metadata is None:
            raise AutomationError(
                f"Metadata catalog is missing '{solution.slug}' for solution file '{solution.file_path}'."
            )

        problem = problems.setdefault(solution.slug, CatalogProblem.from_metadata(metadata))
        try:
            problems[solution.slug] = problem.with_implementation(
                ProblemImplementation(
                    language=solution.language,
                    approach=solution.approach,
                    source_url=solution.source_url,
                )
            )
        except ValueError as error:
            raise AutomationError(str(error)) from error

    return GeneratedCatalog(
        languages=tuple(target.catalog_language() for target in targets),
        problems=tuple(problem for _, problem in sorted(problems.items(), key=lambda item: item[0])),
    )


def _build_solution_record(
    *,
    file_path: str,
    target: LanguageTarget,
    source_url_base: str,
) -> SolutionCommit | None:
    if not target.matches(file_path) or not is_solution_candidate_path(file_path):
        return None

    approach = extract_approach(file_path)
    if approach is None:
        return None

    subject = latest_solution_subject(file_path)
    if subject is None:
        raise AutomationError(
            f"Source file '{file_path}' lives under a solution path but has no solution commit in history."
        )

    parsed = parse_solution_subject(subject)
    if parsed.approach != approach:
        raise AutomationError(
            f"File '{file_path}' uses approach '{approach}' but its latest solution commit declares "
            f"'{parsed.approach}'."
        )

    return SolutionCommit(
        file_path=file_path,
        language=target.language,
        approach=approach,
        slug=parsed.slug,
        source_url=target.source_url(source_url_base, file_path),
    )
