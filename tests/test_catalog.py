from __future__ import annotations

from pathlib import Path

from automation.catalog import build_generated_catalog, collect_solution_records, load_generated_catalog
from automation.config import load_targets
from automation.models import ProblemMetadata


def test_rebuild_matches_committed_generated_catalog() -> None:
    current = load_generated_catalog(Path("_data/problems.yml"))
    targets = load_targets(Path(".github/problem-catalog/targets.yml"))
    solutions = collect_solution_records(
        targets=targets,
        source_url_base="https://github.com/leowajda/eureka/blob/master",
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
        metadata_catalog=metadata_catalog,
        solutions=solutions,
    )

    assert rebuilt == current
