---
name: qmd-setup
description: Set up the project-local QMD index for this LLM Wiki.
disable-model-invocation: true
---

# QMD Setup

Set up a portable QMD search cache for a Git-synchronized LLM Wiki. The checked-in configuration is authoritative for collection scope; the generated SQLite index and downloaded models stay local.

## Steps

1. From the repository root, verify Node.js 22+ or Bun 1+, then check for `qmd`. If it is absent, ask before installing a global package, then install with `npm install -g @tobilu/qmd` or `bun install -g @tobilu/qmd`. This step is complete when `qmd doctor` can inspect the runtime.
2. Inspect `.qmd/index.yml`. Keep collection paths relative and inside the repository, keep shell update hooks absent, and index only compiled concept pages under `wiki/`; `raw/` and `outputs/` remain outside QMD retrieval. This step is complete when the config matches the repository layout without machine-specific paths.
3. Verify `.gitignore` excludes `.qmd/*.sqlite` and `.qmd/*.sqlite-*` while `.qmd/index.yml` remains trackable. This step is complete when `git check-ignore` ignores the generated database but not the YAML config.
4. Run `tools/qmd-update.sh` from any directory. It updates the index, then checks status, the `wiki` collection, its files, and lexical search. Pass `--embed` when semantic retrieval is requested or measured semantic misses justify it; model downloads and vectors are local caches. This step is complete when the script exits successfully; an empty lexical result is valid when the wiki has no concepts.

## Synchronization

Git, Dropbox, or another sync mechanism updates the repository files first; `qmd update` then refreshes the local cache. Do not add a checked-in `update: "git pull ..."` hook: queries must not mutate the working tree, and checked-in shell hooks require QMD trust approval.
