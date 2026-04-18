from __future__ import annotations

from automation.errors import AutomationError
from automation.utils import slugify_title

DIFFICULTY_PREFIX = "difficulty:"
TOPIC_PREFIX = "topic:"
SUPPORTED_DIFFICULTIES = frozenset({"easy", "medium", "hard"})


def build_problem_label_names(
    *,
    difficulty: str,
    categories: tuple[str, ...],
) -> tuple[str, ...]:
    difficulty_slug = slugify_title(difficulty)
    if difficulty_slug not in SUPPORTED_DIFFICULTIES:
        raise AutomationError(f"Unsupported LeetCode difficulty '{difficulty}'.")

    labels = {f"{DIFFICULTY_PREFIX}{difficulty_slug}"}
    labels.update(
        f"{TOPIC_PREFIX}{topic_slug}"
        for topic_slug in (slugify_title(category) for category in categories)
        if topic_slug
    )
    return tuple(sorted(labels))
