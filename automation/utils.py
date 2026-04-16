from __future__ import annotations

import re
from pathlib import PurePosixPath

APPROACHES = frozenset({"iterative", "recursive"})
IGNORED_SOLUTION_FILENAMES = frozenset({"__init__.py"})
NON_SLUG_CHARACTERS = re.compile(r"[^a-zA-Z0-9- ]")


def normalize_path(path: str) -> str:
    return path.strip().replace("\\", "/").removeprefix("./")


def extract_approach(file_path: str) -> str | None:
    for segment in PurePosixPath(normalize_path(file_path)).parts:
        if segment in APPROACHES:
            return segment
    return None


def is_solution_candidate_path(file_path: str) -> bool:
    normalized = normalize_path(file_path)
    return (
        extract_approach(normalized) is not None
        and PurePosixPath(normalized).name not in IGNORED_SOLUTION_FILENAMES
    )


def slugify_title(title: str) -> str:
    normalized = title.replace(" - ", " ")
    return NON_SLUG_CHARACTERS.sub("", normalized).replace(" ", "-").lower()
