import os
from operator import attrgetter
from pathlib import Path

import pandas as pd

from action import Action
from solution import Solution


# ---------------------------------------------------------------------------
# Environment / configuration
# ---------------------------------------------------------------------------


def _require_env(name: str) -> str:
    """Return the value of an environment variable or raise with a clear message."""
    value = os.getenv(name)
    if not value:
        raise RuntimeError(f"Required environment variable '{name}' is not set or empty.")
    return value


def _env_filelist(name: str) -> list[str]:
    """Return a list of file paths from a whitespace-separated env var.

    Returns an empty list when the variable is absent or empty — this is the
    correct behaviour when no files of that type changed in the triggering
    commit.
    """
    return (os.getenv(name) or "").split()


ADDED_FILES: list[str] = _env_filelist("added_files")
CHANGED_FILES: list[str] = _env_filelist("changed_files")
REMOVED_FILES: list[str] = _env_filelist("removed_files")

REPOSITORY: str = _require_env("repository")
SERVER_URL: str = _require_env("server_url")
README: Path = Path(_require_env("readme"))
DATAFRAME: Path = Path(_require_env("dataframe"))
HEADER: Path = Path(_require_env("header"))
GITHUB_OUTPUT: Path = Path(_require_env("GITHUB_OUTPUT"))


# ---------------------------------------------------------------------------
# Build and sort the solution list
# ---------------------------------------------------------------------------

removed_solutions: list[Solution] = [
    Solution(file, Action.REMOVE, SERVER_URL, REPOSITORY) for file in REMOVED_FILES
]
updated_solutions: list[Solution] = [
    Solution(file, Action.UPDATE, SERVER_URL, REPOSITORY) for file in CHANGED_FILES
]
added_solutions: list[Solution] = [
    Solution(file, Action.ADD, SERVER_URL, REPOSITORY) for file in ADDED_FILES
]

all_solutions: list[Solution] = sorted(
    removed_solutions + updated_solutions + added_solutions,
    key=attrgetter("timestamp"),
)


# ---------------------------------------------------------------------------
# Load the dataframe; keep the original state for change-detection at the end
# ---------------------------------------------------------------------------

# original_df is used for change-detection at the end: it has the same shape
# and semantics as the re-grouped mod_df, so .equals() is meaningful.
name_col: str
lang_col: str
original_df: pd.DataFrame = pd.read_csv(DATAFRAME, index_col=0)
name_col, lang_col = original_df.index.name, original_df.columns[0]
original_df = original_df.sort_index()

# Explode space-separated language links into one row per link for processing.
# Use **{lang_col: ...} so the variable value is used as the column name,
# not the string literal "lang_col".
df: pd.DataFrame = original_df.reset_index()
df = df.assign(**{lang_col: df[lang_col].str.split(" ")})
df = df.explode(lang_col)

# Work on an explicit copy so that mutations to mod_df never affect df.
mod_df: pd.DataFrame = df.copy()


# ---------------------------------------------------------------------------
# Apply each solution's action to mod_df
# ---------------------------------------------------------------------------

# Collect solutions that produced a real change; build a new list rather than
# mutating all_solutions mid-iteration (.remove() can silently drop the wrong
# item when duplicates are present).
active_solutions: list[Solution] = []

for solution in all_solutions:
    match solution.action:
        case Action.UNDEFINED:
            print(f"couldn't resolve commit metadata for {solution}, skipping...")

        case Action.ADD:
            prev_entry = mod_df[
                (mod_df[name_col] == solution.host_url)
                & (mod_df[lang_col] == solution.github_url)
            ]
            if prev_entry.empty:
                print(f"adding {solution}")
                frame = pd.DataFrame(
                    [[solution.host_url, solution.github_url]],
                    columns=[name_col, lang_col],
                )
                mod_df = pd.concat([frame, mod_df], ignore_index=True)
                active_solutions.append(solution)
            else:
                print(f"{solution} is already present, skipping...")

        case Action.UPDATE:
            print(f"updating {solution}")
            frame = pd.DataFrame(
                [[solution.host_url, solution.github_url]],
                columns=[name_col, lang_col],
            )
            mod_df = pd.concat([frame, mod_df], ignore_index=True)
            active_solutions.append(solution)

        case Action.REMOVE:
            print(f"removing {solution}")
            mod_df = mod_df[
                (mod_df[name_col] != solution.host_url)
                & (mod_df[lang_col] != solution.github_url)
            ]
            active_solutions.append(solution)


# ---------------------------------------------------------------------------
# Re-group individual language rows back into space-separated cells
# ---------------------------------------------------------------------------

# sorted() inside the aggregation ensures a deterministic URL order so that
# the output CSV/markdown does not produce false diffs across runs.
mod_df = mod_df.groupby(by=name_col, as_index=False)[lang_col].agg(
    lambda x: " ".join(sorted(x))
)


# ---------------------------------------------------------------------------
# Write outputs only when something actually changed
# ---------------------------------------------------------------------------

# Compare against the original CSV state (same shape and semantics).
# Using a consistently indexed and sorted DataFrame on both sides ensures
# that .equals() returns True whenever the content is unchanged.
final_df: pd.DataFrame = mod_df.set_index(name_col).sort_index()

if final_df.equals(original_df):
    raise SystemExit(0)

# Print a human-readable summary to stdout before opening GITHUB_OUTPUT so
# it is clearly not written to the file.
print(f"filtered solutions:\n{', '.join(str(s) for s in active_solutions)}")

details: list[str] = [
    f"{solution.problem_name}: {solution.sha}" for solution in active_solutions
]
noun: str = "change" if len(details) == 1 else "changes"
commit_msg: str = f"ci(docs): update table with latest {noun}\n" + "\n".join(details)

with GITHUB_OUTPUT.open("a") as f:
    print(f"commit_msg<<EOF\n{commit_msg}\nEOF", file=f)

with DATAFRAME.open("w") as f:
    f.write(final_df.to_csv())

header_content: str = HEADER.read_text()
with README.open("w") as f:
    f.write(header_content)
    f.write(final_df.to_markdown(colalign=("center", "center")))
