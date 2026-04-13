from __future__ import annotations

from pathlib import Path
import sys
import unittest

SCRIPTS_DIR = Path(__file__).resolve().parents[1] / ".github" / "workflows" / "scripts"
sys.path.insert(0, str(SCRIPTS_DIR))

from action import Action
from solution import Solution
from update_table import apply_solution_change
from workflow_support import (
    LanguageTarget,
    remove_language_implementations,
    upsert_language_metadata,
)


class WorkflowSupportTest(unittest.TestCase):
    def test_language_target_matches_configured_glob(self) -> None:
        target = LanguageTarget(
            language="python",
            label="Python",
            code_language="python",
            path_prefix="python",
            path_glob="python/src/**/*.py",
            source_url_base="https://github.com/leowajda/eureka/blob/master",
        )

        self.assertTrue(target.matches("python/src/array/iterative/BinarySearch.py"))
        self.assertFalse(target.matches("python/pyproject.toml"))
        self.assertFalse(target.matches("java/src/main/java/array/BinarySearch.java"))

    def test_remove_language_implementations_prunes_empty_problems(self) -> None:
        problems = {
            "binary-search": {
                "name": "Binary Search",
                "url": "https://leetcode.com/problems/binary-search",
                "difficulty": "Easy",
                "categories": ["Array", "Binary Search"],
                "python": {"iterative": "python-url"},
                "java": {"iterative": "java-url"},
            },
            "two-sum": {
                "name": "Two Sum",
                "url": "https://leetcode.com/problems/two-sum",
                "difficulty": "Easy",
                "categories": ["Array"],
                "python": {"iterative": "python-url"},
            },
        }

        cleaned = remove_language_implementations(problems, "python")

        self.assertIn("binary-search", cleaned)
        self.assertNotIn("python", cleaned["binary-search"])
        self.assertNotIn("two-sum", cleaned)

    def test_apply_solution_change_updates_single_language_slice(self) -> None:
        problems = {
            "binary-search": {
                "name": "Binary Search",
                "url": "https://leetcode.com/problems/binary-search",
                "difficulty": "Easy",
                "categories": ["Array", "Binary Search"],
                "python": {"iterative": "old-python-url"},
                "java": {"iterative": "java-url"},
            }
        }
        solution = Solution(
            file_path="python/src/array/iterative/BinarySearch.py",
            action=Action.UPDATE,
            timestamp=1,
            sha="deadbeef",
            problem_name="Binary Search",
            slug="binary-search",
            source_url="new-python-url",
            problem_url="https://leetcode.com/problems/binary-search",
            approach="iterative",
            language="python",
            difficulty="Easy",
            categories=("Array", "Binary Search"),
        )

        changed = apply_solution_change(problems, solution)

        self.assertTrue(changed)
        self.assertEqual(
            problems["binary-search"]["python"]["iterative"], "new-python-url"
        )
        self.assertEqual(problems["binary-search"]["java"]["iterative"], "java-url")

    def test_upsert_language_metadata_overwrites_target_fields_only(self) -> None:
        languages = {
            "python": {
                "label": "Old Python",
                "code_language": "old-python",
                "icon": "python",
            }
        }
        target = LanguageTarget(
            language="python",
            label="Python",
            code_language="python",
            path_prefix="python",
            path_glob="python/src/**/*.py",
            source_url_base="https://github.com/leowajda/eureka/blob/master",
        )

        updated = upsert_language_metadata(languages, target)

        self.assertEqual(updated["python"]["label"], "Python")
        self.assertEqual(updated["python"]["code_language"], "python")
        self.assertEqual(updated["python"]["icon"], "python")


if __name__ == "__main__":
    unittest.main()
