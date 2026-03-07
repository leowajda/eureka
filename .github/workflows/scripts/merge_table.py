import os
import shlex
import subprocess
from functools import reduce
from pathlib import Path

import pandas as pd


# ---------------------------------------------------------------------------
# Environment / configuration
# ---------------------------------------------------------------------------

def _require_env(name: str) -> str:
    value = os.getenv(name)
    if not value:
        raise RuntimeError(f"Required environment variable '{name}' is not set or empty.")
    return value


README: Path = Path(_require_env("readme"))
DATAFRAME: Path = Path(_require_env("dataframe"))
HEADER: Path = Path(_require_env("header"))
INDEX = _require_env("index")
ACTOR = _require_env("actor")
SERVER_URL = _require_env("server_url")
GITHUB_OUTPUT: Path = Path(_require_env("GITHUB_OUTPUT"))

SUBMODULE_PREFIX = "eureka"
REPO_ROOT: Path = Path(".")

# ---------------------------------------------------------------------------
# Load every submodule CSV exactly once
# ---------------------------------------------------------------------------

sub_directories: list[Path] = [
    f for f in REPO_ROOT.iterdir()
    if f.is_dir() and SUBMODULE_PREFIX in f.name
]

# Map each non-index column name -> submodule directory name.
# The dataframe is loaded once here; the same object goes into `dataframes`.
col_to_submodule: dict[str, str] = {}
dataframes: list[pd.DataFrame] = []

for directory in sub_directories:
    df: pd.DataFrame = pd.read_csv(directory / "content" / "data.csv")
    dataframes.append(df)
    col_to_submodule.update(
        {col: directory.name for col in df.columns if col != INDEX}
    )

# ---------------------------------------------------------------------------
# Merge and normalise
# ---------------------------------------------------------------------------

mod_df: pd.DataFrame = reduce(
    lambda left, right: pd.merge(left, right, how="outer", on=INDEX),
    dataframes,
)
mod_df = mod_df.set_index(INDEX).fillna("").sort_index()
cached_df: pd.DataFrame = pd.read_csv(DATAFRAME, index_col=INDEX).fillna("")

if mod_df.equals(cached_df):
    raise SystemExit(0)

# ---------------------------------------------------------------------------
# Determine which columns changed and resolve their submodule commit URLs
# ---------------------------------------------------------------------------

common_cols: pd.Index = cached_df.columns.intersection(mod_df.columns)
new_cols: pd.Index = mod_df.columns.difference(cached_df.columns)

changed_cols: list[str] = [
    col for col in common_cols if not cached_df[col].equals(mod_df[col])
]
changed_cols.extend(new_cols)

# Deduplicate submodules while preserving insertion order so that the commit
# message lists URLs in the same order the columns appear.
changed_submodules: list[str] = list(dict.fromkeys(
    col_to_submodule[col] for col in changed_cols
))

details: list[str] = []
for submodule in changed_submodules:
    result = subprocess.run(
        args=(
            f"git submodule status {shlex.quote(submodule)}"
            f" | awk '{{print $1}}'"
            f" | sed 's/^[-+]//'"
        ),
        text=True,
        check=True,
        shell=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    commit_sha = result.stdout.strip()
    details.append(f"{SERVER_URL}/{ACTOR}/{submodule}/commit/{commit_sha}")

# ---------------------------------------------------------------------------
# Write outputs
# ---------------------------------------------------------------------------

noun = "change" if len(details) == 1 else "changes"
commit_msg = f"ci(docs): update table with latest {noun}\n" + "\n".join(details)

with GITHUB_OUTPUT.open("a") as f:
    print(f"commit_msg<<EOF\n{commit_msg}\nEOF", file=f)

with DATAFRAME.open("w") as f:
    f.write(mod_df.to_csv())

header_content = HEADER.read_text()
with README.open("w") as f:
    f.write(header_content)
    f.write(mod_df.to_markdown(colalign=("center",) * (len(mod_df.columns) + 1)))
