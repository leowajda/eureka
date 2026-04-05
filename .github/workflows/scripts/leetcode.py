from __future__ import annotations

from typing import Any

import requests

GRAPHQL_URL = "https://leetcode.com/graphql"
QUESTION_QUERY = {
    "query": "query questionData($titleSlug: String!) { question(titleSlug: $titleSlug) { difficulty topicTags { name } } }"
}


def fetch_problem_metadata(
    slug: str, session_token: str | None
) -> tuple[str, list[str]]:
    if not slug or not session_token:
        return "", []

    try:
        response = requests.post(
            GRAPHQL_URL,
            json={**QUESTION_QUERY, "variables": {"titleSlug": slug}},
            headers={
                "Content-Type": "application/json",
                "Cookie": f"LEETCODE_SESSION={session_token}",
            },
            timeout=30,
        )
        response.raise_for_status()
        question = _extract_question(response.json())
    except (requests.RequestException, ValueError):
        return "", []

    if not question:
        return "", []

    return question.get("difficulty", ""), [
        tag["name"] for tag in question.get("topicTags", []) if "name" in tag
    ]


def _extract_question(payload: dict[str, Any]) -> dict[str, Any] | None:
    question = payload.get("data", {}).get("question")
    return question if isinstance(question, dict) else None
