from __future__ import annotations

import httpx
import pytest
from automation.errors import AutomationError
from automation.leetcode import LeetCodeClient


def test_leetcode_client_fetches_problem_metadata() -> None:
    transport = httpx.MockTransport(
        lambda request: httpx.Response(
            200,
            json={
                "data": {
                    "question": {
                        "title": "Binary Search",
                        "titleSlug": "binary-search",
                        "difficulty": "Easy",
                        "topicTags": [{"name": "Array"}, {"name": "Binary Search"}],
                    }
                }
            },
        )
    )

    with httpx.Client(transport=transport) as client:
        metadata = LeetCodeClient(client=client, session_token=None).fetch_problem_metadata("binary-search")

    assert metadata.slug == "binary-search"
    assert metadata.name == "Binary Search"
    assert metadata.difficulty == "Easy"
    assert metadata.categories == ("Array", "Binary Search")


def test_leetcode_client_rejects_slug_mismatches() -> None:
    transport = httpx.MockTransport(
        lambda request: httpx.Response(
            200,
            json={
                "data": {
                    "question": {
                        "title": "Binary Search",
                        "titleSlug": "wrong-slug",
                        "difficulty": "Easy",
                        "topicTags": [],
                    }
                }
            },
        )
    )

    with httpx.Client(transport=transport) as client:
        with pytest.raises(AutomationError):
            LeetCodeClient(client=client, session_token=None).fetch_problem_metadata("binary-search")


def test_leetcode_client_fetches_pull_request_metadata() -> None:
    transport = httpx.MockTransport(
        lambda request: httpx.Response(
            200,
            json={
                "data": {
                    "question": {
                        "title": "Binary Search",
                        "titleSlug": "binary-search",
                        "questionFrontendId": "704",
                        "difficulty": "Easy",
                        "topicTags": [{"name": "Array"}, {"name": "Binary Search"}],
                        "similarQuestionList": [
                            {
                                "title": "Search Insert Position",
                                "titleSlug": "search-insert-position",
                                "questionFrontendId": "35",
                            },
                        ],
                    }
                }
            },
        )
    )

    with httpx.Client(transport=transport) as client:
        metadata = LeetCodeClient(client=client, session_token=None).fetch_pull_request_metadata(
            "binary-search"
        )

    assert metadata.slug == "binary-search"
    assert metadata.frontend_id == "704"
    assert metadata.name == "Binary Search"
    assert metadata.related[0].slug == "search-insert-position"
