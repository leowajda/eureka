import pandas as pd
import os
import subprocess
from pathlib import Path
from functools import reduce

README, DATAFRAME, HEADER, INDEX, ACTOR, SERVER_URL = [
    os.getenv(env) for env in ("readme", "dataframe", "header", "index", "actor", "server_url")
]

PATH = Path(".")
SUBMODULE_PREFIX = "eureka"

sub_directories = [f for f in PATH.iterdir() if f.is_dir() and SUBMODULE_PREFIX in f.name]

mod_df = reduce(
    lambda left, right: pd.merge(left, right, how='outer', on=[INDEX]),
    [pd.read_csv(f"./{directory}/content/data.csv") for directory in sub_directories]
)

mod_df = mod_df.set_index(INDEX).fillna('').sort_index()
cached_df = pd.read_csv(DATAFRAME, index_col=INDEX)

if not mod_df.equals(cached_df):

    common_cols = cached_df.columns.intersection(mod_df.columns)
    new_cols = mod_df.columns.difference(cached_df.columns)

    changed_cols = []
    for col in common_cols:
        if not cached_df[col].equals(mod_df[col]):
            changed_cols.append(col)
    changed_cols.extend(new_cols)

    details = []
    for col in changed_cols:
        language = col.lower().strip()
        submodule = f"{SUBMODULE_PREFIX}-{language}"
        completed_process = subprocess.run(
            args=f"git submodule status {submodule} | awk '{{print $1}}' | sed 's/^-//'",
            text=True, check=True, shell=True, stdout=subprocess.PIPE
        )
        commit_sha = completed_process.stdout.strip()
        url = f"{SERVER_URL}/{ACTOR}/{submodule}/commit/{commit_sha}"
        details.append(f"{col}: {url}")

    with open(os.environ['GITHUB_OUTPUT'], 'a') as f:
        commit_msg = f'ci(docs): update table with changes from {", ".join(details)}'
        print(f"commit_msg={commit_msg}", file=f)

    with open(DATAFRAME, 'w') as f:
        f.write(mod_df.to_csv())

    with open(README, 'w') as f:
        with open(HEADER, 'r') as s:
            content = s.read()
        f.write(content)
        f.write(mod_df.to_markdown(colalign=("center",) * len(mod_df.columns)))
