from __future__ import annotations

import argparse
import sys
from pathlib import Path

from automation.errors import AutomationError
from automation.sync import replay_catalog, sync_catalog


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
        required=True,
        help="Path to the targets configuration file.",
    )
    sync.add_argument(
        "--session-token",
        default=None,
        help="Optional LEETCODE_SESSION token used for authenticated LeetCode requests.",
    )
    sync.add_argument(
        "--catalog-path",
        type=Path,
        required=True,
        help="Path to the generated problem catalog artifact.",
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
        required=True,
        help="Path to the targets configuration file.",
    )
    replay.add_argument(
        "--session-token",
        default=None,
        help="Optional LEETCODE_SESSION token used for authenticated LeetCode requests.",
    )
    replay.add_argument(
        "--catalog-path",
        type=Path,
        required=True,
        help="Path to the generated problem catalog artifact.",
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
