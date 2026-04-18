from __future__ import annotations

from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
DEFAULT_TARGETS_PATH = REPO_ROOT / ".github" / "problem-catalog" / "targets.yml"
DEFAULT_CATALOG_PATH = REPO_ROOT / "data" / "problems.yml"
