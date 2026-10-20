# Working agreement for Claude Code

Claude Code reads this file at the start of every session in this repository. These are the rules for building Mallard with it. If a git-ignored `SESSION.md` exists in the repository root, read it first: it holds the current state of the work.

---

## Who does what

| I (Jitse-Jan) | Claude Code |
|---|---|
| Write the code, by hand | Proposes the next small step, explains it, and reviews what I wrote |
| Set scope and direction, decide trade-offs | Presents options with a recommendation |
| Review and merge every pull request | Drafts issues and pull request descriptions |
| Decide when to stop | Says honestly when something didn't work |

When I ask Claude Code to make a change, it works one small branch at a time, shows the code and the commands it ran, and waits for my go-ahead before pushing or opening a pull request. It never merges, force-pushes, or rewrites history, and asks before anything hard to undo or outside this repository.

---

## Code

- **Simple over clever.** The smallest change that does the job, in code that reads like the rest of the repository.
- **Named constants instead of magic numbers**, with a comment explaining *why* the value was chosen.
- **Comments only for the non-obvious why.**
- **Python from `.python-version`**, managed with uv: `uv add` for dependencies, never edit `uv.lock` by hand. ruff for lint and format, strict mypy over `src`, `tests`, and `tasks.py`.
- **Shared commands through invoke**, the same ones CI runs: `uv run invoke lint`, `uv run invoke test`, `uv run invoke format`.
- **No one-off scripts where a test will do.**
- **Environment from `.env`:** `uv run --env-file .env ...`, which also works in fish.

## Tests

- **Everything we build comes with tests.** Every behaviour change has a test that fails on the old code, and Claude Code checks that it does.
- **Assert results, not the absence of errors:** exact rows, columns, and counts.
- **Unit tests run offline** with fixtures or fakes, such as a small git repository made in `tmp_path` or sample `.jsonl` files. No live services in unit tests or CI.
- **Tests that need the real lake are marked `lake`** and skip when its credentials are missing. Run them with `uv run --env-file .env invoke test`.

## Git and pull requests

- **Issue first.** Every change traces back to a GitHub issue. Branch from `main` as `<type>/<issue>-<short-description>`.
- **Conventional Commits** with only these types: `feat`, `fix`, `refactor`, `test`, `docs`, `chore`, `perf` (CI changes are `chore:`). A body explains *why*.
- **Pull request descriptions are one or two short paragraphs:** why, then what changed, then `Closes #<issue>` or `Part of #<issue>`.
- **Check that each commit succeeded** before the next step; pre-commit hooks can reject a commit silently in a chained command.
- **Before deleting a branch, confirm its commits are on `main`.**
- **No AI attribution** (`Co-Authored-By` trailers or "Generated with" footers) and no emoji in commits, pull requests, issues, or comments.

## Built in the open

This repository and its GitHub Action logs are public.

- **Secrets live only in `.env` and GitHub Actions secrets.** `.env` is git-ignored; `.env.example` lists every variable with a placeholder, so anyone can run Mallard with their own accounts.
- **Never print SQL, URLs, or connection strings that contain credentials**, locally or in CI.
- **Keep private and client repository names out of** code, issues, commits, and logs.

## Data

- **Loads are idempotent.** Sources merge on their primary keys; re-running a load must not change row counts.
- **Privacy:** never store commit message text, Claude Code message text, tool inputs, or tool output.
- **Layer discipline:** raw (loaded by dlt) -> `stage` -> `curate`. Stage reads only from sources, curate only from stage.
- **The lake's data path never changes after the first load:** DuckLake stores it in the catalog.
- **DuckDB and dlt must attach the lake with the same `METADATA_SCHEMA`**, or they silently use two catalogs.

## Documentation

- **README is for running and testing.** Decisions go in `docs/decisions.md` as short ADRs, collected as we go.
- **Write in my voice, as documentation:** first person, plain sentences, headings as short phrases, bold lead-ins. Every number in the docs must be reproducible.
