import os
import subprocess

SUBMODULE_PREFIX = "eureka"
SERVER_URL, ACTOR = [os.getenv(env) for env in ("server_url", "actor")]

completed_process = subprocess.run(
    args=f"git submodule status | awk '{{print $1, $2}}'",
    text=True, check=True, shell=True, stdout=subprocess.PIPE
)

details = []
for metadata in completed_process.stdout.splitlines():
    if metadata.startswith('-') or metadata.startswith('U'):
        continue

    commit_sha, submodule = metadata.split()
    commit_sha = commit_sha.replace('+', '')
    language = submodule.replace(f"{SUBMODULE_PREFIX}-", "")
    url = f"{SERVER_URL}/{ACTOR}/{submodule}/commit/{commit_sha}"
    details.append(url)

with open(os.environ['GITHUB_OUTPUT'], 'a') as f:
    noun = "submodule" if len(details) == 1 else "submodules"
    commit_msg = f'ci(docs): update lang {noun} to latest version\n' + "\n".join(details)
    print(f'commit_msg<<EOF\n{commit_msg}\nEOF', file=f)
