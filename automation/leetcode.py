from __future__ import annotations

from collections.abc import Iterable, Mapping
from typing import Any, Final

import httpx
from tenacity import retry, retry_if_exception_type, stop_after_attempt, wait_exponential

from automation.errors import AutomationError
from automation.models import ProblemMetadata

GRAPHQL_URL: Final = "https://leetcode.com/graphql"
QUESTION_QUERY: Final[dict[str, str]] = {
    "query": (
        "query questionData($titleSlug: String!) { "
        "question(titleSlug: $titleSlug) { title titleSlug difficulty topicTags { name } } }"
    )
}


def fetch_problem_metadata_map(
    slugs: Iterable[str],
    session_token: str | None,
) -> dict[str, ProblemMetadata]:
    requested_slugs = tuple(sorted(set(slugs)))
    if not requested_slugs:
        return {}

    with httpx.Client(timeout=30.0) as client:
        leetcode = LeetCodeClient(client=client, session_token=session_token)
        return {slug: leetcode.fetch_problem_metadata(slug) for slug in requested_slugs}


class LeetCodeClient:
    def __init__(self, *, client: httpx.Client, session_token: str | None) -> None:
        self._client = client
        self._session_token = session_token

    @retry(
        retry=retry_if_exception_type((httpx.HTTPError, AutomationError)),
        wait=wait_exponential(multiplier=1, min=1, max=8),
        stop=stop_after_attempt(3),
        reraise=True,
    )
    def fetch_problem_metadata(self, slug: str) -> ProblemMetadata:
        response = self._client.post(
            GRAPHQL_URL,
            json={**QUESTION_QUERY, "variables": {"titleSlug": slug}},
            headers=self._headers(),
        )
        response.raise_for_status()

        question = _extract_question(response.json(), slug)
        returned_slug = question.get("titleSlug")
        if returned_slug != slug:
            raise AutomationError(f"LeetCode returned slug '{returned_slug}' while fetching '{slug}'.")

        return ProblemMetadata(
            slug=slug,
            name=str(question["title"]).strip(),
            difficulty=str(question["difficulty"]).strip(),
            categories=_extract_categories(question),
        )

    def _headers(self) -> dict[str, str]:
        headers = {"Content-Type": "application/json"}
        if self._session_token:
            headers["Cookie"] = f"LEETCODE_SESSION={self._session_token}"
        return headers


def _extract_question(payload: Mapping[str, Any], slug: str) -> Mapping[str, Any]:
    data = payload.get("data", {})
    if not isinstance(data, Mapping):
        raise AutomationError(f"LeetCode response for '{slug}' does not contain a valid 'data' object.")

    question = data.get("question")
    if not isinstance(question, Mapping):
        raise AutomationError(f"LeetCode did not return question data for '{slug}'.")
    return question


def _extract_categories(question: Mapping[str, Any]) -> tuple[str, ...]:
    topic_tags = question.get("topicTags", [])
    if not isinstance(topic_tags, list):
        raise AutomationError("LeetCode returned an invalid topicTags payload.")

    return tuple(
        name.strip()
        for tag in topic_tags
        if isinstance(tag, Mapping)
        for name in [tag.get("name")]
        if isinstance(name, str) and name.strip()
    )
