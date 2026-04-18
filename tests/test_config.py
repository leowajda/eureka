from __future__ import annotations

from automation.config import load_solution_action_labels, load_targets
from automation.paths import DEFAULT_SOLUTION_ACTION_LABELS_PATH, DEFAULT_TARGETS_PATH


def test_load_targets_uses_committed_configuration() -> None:
    targets = load_targets(DEFAULT_TARGETS_PATH)

    assert tuple(target.language for target in targets) == ("java", "scala", "python", "cpp")


def test_load_solution_action_labels_uses_committed_configuration() -> None:
    action_labels = load_solution_action_labels(DEFAULT_SOLUTION_ACTION_LABELS_PATH)

    assert action_labels == {
        "add": "Add",
        "update": "Update",
        "remove": "Remove",
    }
