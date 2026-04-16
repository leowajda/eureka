from __future__ import annotations

from pathlib import Path

from pydantic import ValidationError

from automation.errors import AutomationError
from automation.models import LanguageTarget, TargetsConfig
from automation.yamlio import load_yaml


def load_targets(path: Path) -> tuple[LanguageTarget, ...]:
    try:
        payload = load_yaml(path)
        return TargetsConfig.model_validate(payload).targets
    except (OSError, TypeError, ValueError, ValidationError) as error:
        raise AutomationError(f"Could not load target configuration from '{path}': {error}") from error
