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
4. Run `qmd update`, then verify `qmd status`, `qmd collection show wiki`, and `qmd ls wiki`. QMD documentation conflicts on whether collection paths must be absolute while its project-local examples permit `./docs`; if this installed version rejects `./wiki`, stop and report the incompatibility rather than committing an absolute path. This step is complete when QMD resolves the collection to this repository's `wiki/` directory.
5. Run a lexical smoke search with `qmd search -c wiki --json -n 5 "retrieval"`. An empty result is valid when the wiki has no concepts. Run `qmd embed -c wiki` only when semantic retrieval is requested or measured semantic misses justify it; model downloads and vectors are local caches. This step is complete when lexical search executes and any requested embedding finishes.

## Synchronization

Git, Dropbox, or another sync mechanism updates the repository files first; `qmd update` then refreshes the local cache. Do not add a checked-in `update: "git pull ..."` hook: queries must not mutate the working tree, and checked-in shell hooks require QMD trust approval.
