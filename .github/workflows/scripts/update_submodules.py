from __future__ import annotations

from pathlib import Path

from workflow_support import require_env, run_git, write_output

SUBMODULE_PREFIX = "eureka"


def main() -> None:
    server_url = require_env("server_url")
    actor = require_env("actor")
    github_output = Path(require_env("GITHUB_OUTPUT"))

    details: list[str] = []
    for line in run_git("submodule", "status").splitlines():
        if not line.startswith("+"):
            continue

        commit_sha, submodule = line.split(maxsplit=1)
        if not submodule.startswith(SUBMODULE_PREFIX):
            continue

        details.append(
            f"{server_url}/{actor}/{submodule}/commit/{commit_sha.lstrip('+')}"
        )

    if not details:
        raise SystemExit(0)

    noun = "submodule" if len(details) == 1 else "submodules"
    write_output(
        github_output,
        "commit_msg",
        f"ci(docs): update lang {noun} to latest version\n" + "\n".join(details),
    )


if __name__ == "__main__":
    main()
