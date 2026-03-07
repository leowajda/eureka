import os
import subprocess
from pathlib import Path


def _require_env(name: str) -> str:
    value = os.getenv(name)
    if not value:
        raise RuntimeError(f"Required environment variable '{name}' is not set or empty.")
    return value


SERVER_URL = _require_env("server_url")
ACTOR = _require_env("actor")
GITHUB_OUTPUT: Path = Path(_require_env("GITHUB_OUTPUT"))

SUBMODULE_PREFIX = "eureka"

result = subprocess.run(
    args="git submodule status | awk '{print $1, $2}'",
    text=True,
    check=True,
    shell=True,
    stdout=subprocess.PIPE,
    stderr=subprocess.PIPE,
)

details: list[str] = []
for line in result.stdout.splitlines():
    if not line.startswith("+"):
        continue

    commit_sha, submodule = line.split(maxsplit=1)
    commit_sha = commit_sha.lstrip("+")

    if not submodule.startswith(SUBMODULE_PREFIX):
        continue

    url = f"{SERVER_URL}/{ACTOR}/{submodule}/commit/{commit_sha}"
    details.append(url)

if not details:
    raise SystemExit(0)

noun = "submodule" if len(details) == 1 else "submodules"
commit_msg = f"ci(docs): update lang {noun} to latest version\n" + "\n".join(details)

with GITHUB_OUTPUT.open("a") as f:
    print(f"commit_msg<<EOF\n{commit_msg}\nEOF", file=f)
