from __future__ import annotations

import re
from dataclasses import dataclass

from automation.errors import AutomationError
from automation.utils import slugify_title

SOLUTION_SUBJECT = re.compile(
    r"^solution\(leetcode\): "
    r"(?P<action>add|update) "
    r"(?P<approach>iterative|recursive) "
    r"'(?P<title>[^']+)'$"
)


@dataclass(frozen=True)
class ParsedSolutionSubject:
    action: str
    approach: str
    slug: str


def parse_solution_subject(subject: str) -> ParsedSolutionSubject:
    match = SOLUTION_SUBJECT.match(subject.strip())
    if not match:
        raise AutomationError(
            "Solution commits must follow "
            "\"solution(leetcode): <add|update> <iterative|recursive> 'Problem Title'\"."
        )

    return ParsedSolutionSubject(
        action=match.group("action"),
        approach=match.group("approach"),
        slug=slugify_title(match.group("title")),
    )
