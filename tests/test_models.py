from __future__ import annotations

import pytest
from automation.models import CatalogProblem, GeneratedCatalog, ProblemImplementation, ProblemMetadata


def test_generated_catalog_round_trips_through_payload() -> None:
    catalog = GeneratedCatalog.from_payload(
        {
            "languages": {
                "python": {"label": "Python", "code_language": "python"},
            },
            "problems": {
                "binary-search": {
                    "name": "Binary Search",
                    "url": "https://leetcode.com/problems/binary-search",
                    "difficulty": "Easy",
                    "categories": ["Array", "Binary Search"],
                    "python": {
                        "iterative": "https://example.com/python/src/array/iterative/BinarySearch.py",
                    },
                }
            },
        }
    )

    assert GeneratedCatalog.from_payload(catalog.to_payload()) == catalog


def test_problem_rejects_duplicate_implementations() -> None:
    problem = CatalogProblem.from_metadata(
        ProblemMetadata(
            slug="binary-search",
            name="Binary Search",
            difficulty="Easy",
            categories=("Array", "Binary Search"),
        )
    )
    implementation = ProblemImplementation(
        language="python",
        approach="iterative",
        source_url="https://example.com/python/src/array/iterative/BinarySearch.py",
    )

    with pytest.raises(ValueError):
        problem.with_implementation(implementation).with_implementation(implementation)
