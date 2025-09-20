import os
from action import Action
from solution import Solution
import pandas as pd

ADDED_FILES, CHANGED_FILES, REMOVED_FILES = [
    os.getenv(env).split() for env in ("added_files", "changed_files", "removed_files")
]

REPOSITORY, SERVER_URL, README, DATAFRAME, HEADER = [
    os.getenv(env) for env in ("repository", "server_url", "readme", "dataframe", "header")
]

removed_solutions = [Solution(file, Action.REMOVE, SERVER_URL, REPOSITORY) for file in REMOVED_FILES]
updated_solutions = [Solution(file, Action.UPDATE, SERVER_URL, REPOSITORY) for file in CHANGED_FILES]
added_solutions = [Solution(file, Action.ADD, SERVER_URL, REPOSITORY) for file in ADDED_FILES]

solutions = sorted(removed_solutions + updated_solutions + added_solutions, key=lambda x: x.timestamp)

df = pd.read_csv(DATAFRAME)
name_col, lang_col = df.columns
df = df.assign(lang_col=df[lang_col].str.split(' '))
df = df.explode(lang_col)
mod_df = df

for solution in solutions[:]:
    match solution.action:
        case Action.UNDEFINED:
            print(f"couldn't resolve commit metadata, for {solution} skipping...")
            solutions.remove(solution)
        case Action.ADD:
            prev_entry = mod_df[(mod_df[name_col] == solution.host_url) & (mod_df[lang_col] == solution.github_url)]
            if prev_entry.empty:
                print(f"adding ${solution}")
                frame = pd.DataFrame([[solution.host_url, solution.github_url]], columns=[name_col, lang_col])
                mod_df = pd.concat([frame, mod_df], ignore_index=True)
            else:
                print(f"${solution} is already present, skipping...")
                solutions.remove(solution)
        case Action.UPDATE:
            print(f"updating {solution}")
            frame = pd.DataFrame([[solution.host_url, solution.github_url]], columns=[name_col, lang_col])
            mod_df = pd.concat([frame, mod_df], ignore_index=True)
        case Action.REMOVE:
            print(f"removing {solution}")
            mod_df = mod_df[(mod_df[name_col] != solution.host_url) & (mod_df[lang_col] != solution.github_url)]

mod_df = mod_df.groupby(by=name_col, as_index=False)
mod_df = mod_df[lang_col].agg(lambda x: set(x))
mod_df[lang_col] = mod_df[lang_col].apply(' '.join)

if not mod_df.equals(df):
    with open(os.environ['GITHUB_OUTPUT'], 'a') as f:
        print(f'filtered solutions: \n{", ".join([str(solution) for solution in solutions])}')
        details = [f"{solution.problem_name}: {solution.sha}" for solution in solutions]
        noun = "change" if len(details) == 1 else "changes"
        commit_msg = f'ci(docs): update table with latest {noun}\n' + "\n".join(details)
        print(f"commit_msg={commit_msg}", file=f)

    mod_df = mod_df.set_index(keys=[name_col]).sort_index()
    with open(DATAFRAME, 'w') as f:
        f.write(mod_df.to_csv())

    with open(README, 'w') as f:
        with open(HEADER, 'r') as s:
            content = s.read()
        f.write(content)
        f.write(mod_df.to_markdown(colalign=("center", "center")))
