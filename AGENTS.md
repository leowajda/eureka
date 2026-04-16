# Eureka

## Architecture

- `java/`, `scala/`, `python/`, `cpp/`: solution trees + per-language build files.
- `automation/`: Python CLI used by CI/CD.
- `.github/problem-catalog/targets.yml`: language registry.
- `_data/problems.yml`: generated problem catalog and cache.
- `sync-problem-catalog.yml`: incremental update on `master`.
- `replay-problem-catalog.yml`: manual full rebuild.
- `validate-repository.yml`: lint, tests, compile/build checks.

## Add A Language

1. Add a new root folder with its own buildable source layout.
2. Add one entry to `.github/problem-catalog/targets.yml`:
   `language`, `label`, `code_language`, `path_prefix`, `path_glob`.
3. Add the new path to `.github/workflows/sync-problem-catalog.yml`.
4. Add validation/build steps to `.github/workflows/validate-repository.yml`.
5. Keep solution files under the target path and commit them with `solution(...)`.
