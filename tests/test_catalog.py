from __future__ import annotations

from automation.catalog import build_generated_catalog, collect_solution_records, load_generated_catalog
from automation.config import load_targets
from automation.models import ProblemMetadata
from automation.paths import DEFAULT_CATALOG_PATH, DEFAULT_TARGETS_PATH


def test_rebuild_matches_committed_generated_catalog() -> None:
    current = load_generated_catalog(DEFAULT_CATALOG_PATH)
    targets = load_targets(DEFAULT_TARGETS_PATH)
    solutions = collect_solution_records(
        targets=targets,
    )
    metadata_catalog = {
        problem.slug: ProblemMetadata(
            slug=problem.slug,
            name=problem.name,
            difficulty=problem.difficulty,
            categories=problem.categories,
        )
        for problem in current.problems
    }
    rebuilt = build_generated_catalog(
        targets=targets,
        source_url_base=current.source_url_base,
        metadata_catalog=metadata_catalog,
        solutions=solutions,
    )

    assert rebuilt == current
