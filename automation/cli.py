from __future__ import annotations

import argparse
import sys
from pathlib import Path

from automation.errors import AutomationError
from automation.paths import DEFAULT_CATALOG_PATH, DEFAULT_TARGETS_PATH
from automation.prs import create_and_write_pull_request_plan
from automation.sync import replay_catalog, sync_catalog
from automation.validation import validate_commit_range


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="python -m automation")
    subparsers = parser.add_subparsers(dest="command", required=True)

    sync = subparsers.add_parser("sync")
    sync.add_argument(
        "--source-url-base",
        required=True,
        help="Base URL used when generating source links inside the problem catalog.",
    )
    sync.add_argument(
        "--targets-path",
        type=Path,
        default=DEFAULT_TARGETS_PATH,
        help=f"Path to the targets configuration file. Defaults to '{DEFAULT_TARGETS_PATH}'.",
    )
    sync.add_argument(
        "--session-token",
        default=None,
        help="Optional LEETCODE_SESSION token used for authenticated LeetCode requests.",
    )
    sync.add_argument(
        "--catalog-path",
        type=Path,
        default=DEFAULT_CATALOG_PATH,
        help=f"Path to the generated problem catalog artifact. Defaults to '{DEFAULT_CATALOG_PATH}'.",
    )
    sync.add_argument(
        "--base",
        default=None,
        help="Base revision used to compute incremental changes.",
    )
    sync.add_argument(
        "--head",
        default="HEAD",
        help="Head revision used to compute incremental changes.",
    )

    replay = subparsers.add_parser("replay")
    replay.add_argument(
        "--source-url-base",
        required=True,
        help="Base URL used when generating source links inside the problem catalog.",
    )
    replay.add_argument(
        "--targets-path",
        type=Path,
        default=DEFAULT_TARGETS_PATH,
        help=f"Path to the targets configuration file. Defaults to '{DEFAULT_TARGETS_PATH}'.",
    )
    replay.add_argument(
        "--session-token",
        default=None,
        help="Optional LEETCODE_SESSION token used for authenticated LeetCode requests.",
    )
    replay.add_argument(
        "--catalog-path",
        type=Path,
        default=DEFAULT_CATALOG_PATH,
        help=f"Path to the generated problem catalog artifact. Defaults to '{DEFAULT_CATALOG_PATH}'.",
    )

    create_pull_request = subparsers.add_parser("create-solution-pr")
    create_pull_request.add_argument(
        "--base-branch",
        default="master",
        help="Base branch the pull request should target. Defaults to 'master'.",
    )
    create_pull_request.add_argument(
        "--head-branch",
        required=True,
        help="Head branch that will back the pull request.",
    )
    create_pull_request.add_argument(
        "--head-revision",
        default="HEAD",
        help="Revision used to compute solution changes. Defaults to 'HEAD'.",
    )
    create_pull_request.add_argument(
        "--session-token",
        default=None,
        help="Optional LEETCODE_SESSION token used for authenticated LeetCode requests.",
    )
    create_pull_request.add_argument(
        "--targets-path",
        type=Path,
        default=DEFAULT_TARGETS_PATH,
        help=f"Path to the targets configuration file. Defaults to '{DEFAULT_TARGETS_PATH}'.",
    )
    create_pull_request.add_argument(
        "--output-dir",
        type=Path,
        required=True,
        help="Directory where the generated pull request payload files will be written.",
    )

    validate_commits = subparsers.add_parser("validate-commits")
    validate_commits.add_argument(
        "--base",
        required=True,
        help="Base revision used to determine which commit subjects should be validated.",
    )
    validate_commits.add_argument(
        "--head",
        required=True,
        help="Head revision used to determine which commit subjects should be validated.",
    )

    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    try:
        if args.command == "sync":
            return _handle_sync(args)
        if args.command == "replay":
            return _handle_replay(args)
        if args.command == "create-solution-pr":
            return _handle_create_solution_pr(args)
        if args.command == "validate-commits":
            return _handle_validate_commits(args)
        raise AutomationError(f"Unsupported command: {args.command}")
    except AutomationError as error:
        print(f"error: {error}", file=sys.stderr)
        return 1


def _handle_sync(args: argparse.Namespace) -> int:
    sync_catalog(
        targets_path=args.targets_path,
        catalog_path=args.catalog_path,
        source_url_base=args.source_url_base,
        base_revision=args.base,
        head_revision=args.head,
        session_token=args.session_token,
    )
    print(f"sync: wrote {args.catalog_path}")
    return 0


def _handle_replay(args: argparse.Namespace) -> int:
    replay_catalog(
        targets_path=args.targets_path,
        catalog_path=args.catalog_path,
        source_url_base=args.source_url_base,
        session_token=args.session_token,
    )
    print(f"replay: wrote {args.catalog_path}")
    return 0


def _handle_create_solution_pr(args: argparse.Namespace) -> int:
    plan = create_and_write_pull_request_plan(
        targets_path=args.targets_path,
        base_branch=args.base_branch,
        head_branch=args.head_branch,
        head_revision=args.head_revision,
        session_token=args.session_token,
        output_dir=args.output_dir,
    )
    print(f"create-solution-pr: wrote {args.output_dir}")
    print(f"title: {plan.title}")
    return 0


def _handle_validate_commits(args: argparse.Namespace) -> int:
    validate_commit_range(
        base_revision=args.base,
        head_revision=args.head,
    )
    print("validate-commits: ok")
    return 0
