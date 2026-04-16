from __future__ import annotations

from automation.models import (
    CatalogLanguage,
    CatalogProblem,
    GeneratedCatalog,
    LanguageTarget,
    ProblemImplementation,
    ProblemMetadata,
    SolutionCommit,
)
from automation.sync import ChangeAction, SolutionChange, merge_incremental_catalog


def test_incremental_merge_reuses_existing_metadata_without_fetch() -> None:
    current = GeneratedCatalog(
        languages=(CatalogLanguage(name="java", label="Java", code_language="java"),),
        problems=(
            CatalogProblem(
                slug="binary-search",
                name="Binary Search",
                url="https://leetcode.com/problems/binary-search",
                difficulty="Easy",
                categories=("Array", "Binary Search"),
                implementations=(
                    ProblemImplementation(
                        language="java",
                        approach="iterative",
                        source_url="https://example.com/java/BinarySearch.java",
                    ),
                ),
            ),
        ),
    )
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
    changes = (
        SolutionChange(
            action=ChangeAction.ADD,
            solution=SolutionCommit(
                file_path="python/src/array/iterative/BinarySearch.py",
                language="python",
                approach="iterative",
                slug="binary-search",
                source_url="https://example.com/python/BinarySearch.py",
            ),
        ),
    )

    merged = merge_incremental_catalog(
        current_catalog=current,
        targets=targets,
        session_token=None,
        changes=changes,
    )

    (problem,) = merged.problems
    assert problem.slug == "binary-search"
    assert problem.name == "Binary Search"
    assert [implementation.language for implementation in problem.implementations] == ["java", "python"]


def test_incremental_merge_rehomes_changed_solution() -> None:
    current = GeneratedCatalog(
        languages=(CatalogLanguage(name="python", label="Python", code_language="python"),),
        problems=(
            CatalogProblem(
                slug="old-problem",
                name="Old Problem",
                url="https://leetcode.com/problems/old-problem",
                difficulty="Easy",
                categories=("Array",),
                implementations=(
                    ProblemImplementation(
                        language="python",
                        approach="iterative",
                        source_url="https://example.com/python/Example.py",
                    ),
                ),
            ),
        ),
    )
    targets = (
        LanguageTarget(
            language="python",
            label="Python",
            code_language="python",
            path_prefix="python",
            path_glob="python/src/**/*.py",
        ),
    )
    changes = (
        SolutionChange(
            action=ChangeAction.UPDATE,
            solution=SolutionCommit(
                file_path="python/src/array/iterative/Example.py",
                language="python",
                approach="iterative",
                slug="binary-search",
                source_url="https://example.com/python/Example.py",
            ),
        ),
    )

    merged = merge_incremental_catalog(
        current_catalog=current,
        targets=targets,
        session_token=None,
        changes=changes,
        metadata_loader=lambda slugs, session_token: {
            "binary-search": ProblemMetadata(
                slug="binary-search",
                name="Binary Search",
                difficulty="Easy",
                categories=("Array", "Binary Search"),
            )
        },
    )

    (problem,) = merged.problems
    assert problem.slug == "binary-search"
    assert problem.implementations[0].source_url == "https://example.com/python/Example.py"


def test_incremental_merge_fetches_only_missing_slugs() -> None:
    current = GeneratedCatalog(
        languages=(CatalogLanguage(name="java", label="Java", code_language="java"),),
        problems=(
            CatalogProblem(
                slug="binary-search",
                name="Binary Search",
                url="https://leetcode.com/problems/binary-search",
                difficulty="Easy",
                categories=("Array", "Binary Search"),
                implementations=(
                    ProblemImplementation(
                        language="java",
                        approach="iterative",
                        source_url="https://example.com/java/BinarySearch.java",
                    ),
                ),
            ),
        ),
    )
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
    changes = (
        SolutionChange(
            action=ChangeAction.ADD,
            solution=SolutionCommit(
                file_path="python/src/array/iterative/BinarySearch.py",
                language="python",
                approach="iterative",
                slug="binary-search",
                source_url="https://example.com/python/BinarySearch.py",
            ),
        ),
        SolutionChange(
            action=ChangeAction.ADD,
            solution=SolutionCommit(
                file_path="java/src/main/java/array/iterative/TwoSum.java",
                language="java",
                approach="iterative",
                slug="two-sum",
                source_url="https://example.com/java/TwoSum.java",
            ),
        ),
    )
    captured: list[set[str]] = []

    merged = merge_incremental_catalog(
        current_catalog=current,
        targets=targets,
        session_token=None,
        changes=changes,
        metadata_loader=lambda slugs, session_token: captured.append(set(slugs)) or {
            "two-sum": ProblemMetadata(
                slug="two-sum",
                name="Two Sum",
                difficulty="Easy",
                categories=("Array", "Hash Table"),
            )
        },
    )

    assert captured == [{"two-sum"}]
    assert {problem.slug for problem in merged.problems} == {"binary-search", "two-sum"}
