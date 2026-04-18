from __future__ import annotations

from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
DEFAULT_AUTOMATION_CONFIG_DIR = REPO_ROOT / ".github" / "automation"
DEFAULT_TARGETS_PATH = DEFAULT_AUTOMATION_CONFIG_DIR / "targets.yml"
DEFAULT_SOLUTION_ACTION_LABELS_PATH = DEFAULT_AUTOMATION_CONFIG_DIR / "solution-actions.yml"
DEFAULT_CATALOG_PATH = REPO_ROOT / "data" / "problems.yml"
