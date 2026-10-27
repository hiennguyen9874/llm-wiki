---
type: Concept
title: "Axis Model Zoo CI, linting, Renovate and contribution rules"
description: "How axis-model-zoo is linted and maintained: super-linter workflow, Markdown/YAML/Hadolint/editorconfig rules, Renovate policy (Dockerfiles excluded), CODEOWNERS, contribution process and local lint recipe, plus the configuration drifts found."
tags: [edge-ai, axis, model-zoo, ci, super-linter, renovate, contributing, maintenance]
status: stable
created: 2026-10-27
generated: { by: llm-wiki-agent/1, at: 2026-10-27T08:30:00Z }
stale_after: 2027-04-30
sources:
  - id: mz-readme
    resource: ../raw/axis-model-zoo/README.md
    scope: ../raw/axis-model-zoo/
    kind: code
    revision: "v1.0.7-42-g66bf5ea (66bf5ea7fc1d14b21e2e0d67db5205f02528e6f8, 2026-10-09)"
    title: "AxisCommunications/axis-model-zoo — README (git checkout)"
  - id: mz-linter
    resource: ../raw/axis-model-zoo/.github/workflows/linter.yml
    scope: ../raw/axis-model-zoo/
    kind: code
    revision: "v1.0.7-42-g66bf5ea"
    title: "linter.yml — super-linter workflow"
  - id: mz-renovate
    resource: ../raw/axis-model-zoo/renovate.json
    scope: ../raw/axis-model-zoo/
    kind: code
    revision: "v1.0.7-42-g66bf5ea"
    title: "renovate.json"
  - id: mz-contributing
    resource: ../raw/axis-model-zoo/CONTRIBUTING.md
    scope: ../raw/axis-model-zoo/
    kind: code
    revision: "v1.0.7-42-g66bf5ea"
    title: "CONTRIBUTING.md"
  - id: mz-lintcfg
    resource: ../raw/axis-model-zoo/.markdownlint.yml
    scope: ../raw/axis-model-zoo/
    kind: code
    revision: "v1.0.7-42-g66bf5ea"
    title: "Lint and editor configuration (.markdownlint.yml, .yaml-lint.yml, .hado-lint.yml, .editorconfig, .vscode/)"
  - id: mz-gitignore
    resource: ../raw/axis-model-zoo/.gitignore
    scope: ../raw/axis-model-zoo/
    kind: code
    revision: "v1.0.7-42-g66bf5ea"
    title: ".gitignore"
---

# Axis Model Zoo CI, linting, Renovate and contribution rules

The [Axis Model Zoo](axis-model-zoo-repository.md) has two GitHub Actions workflows that matter for code quality and one for measuring speed. `linter.yml` runs the slim **super-linter** on every push, pull request and manual dispatch; Renovate keeps dependencies current; contributors follow a fork, conventional-commit, pull-request flow. Everything here is **Observed** by reading the configuration; no workflow ran. The speed workflow is covered in [speed pipeline](axis-model-zoo-speed-benchmark-pipeline.md).

## Lint workflow

- **Trigger and scope:** `push`, `pull_request`, `workflow_dispatch`; `permissions: contents: read`; checkout with `fetch-depth: 0`; `VALIDATE_ALL_CODEBASE: true`, default branch `main`.[^mz-linter]
- **Validators enabled:** `BASH`, `DOCKERFILE_HADOLINT`, `MARKDOWN`, `SHELL_SHFMT`, `YAML`. Rule files: `.markdownlint.yml`, `.hado-lint.yml`, `.yaml-lint.yml`.[^mz-linter]
- **Actions are pinned by commit SHA** with version comments (checkout v7.0.1, super-linter slim v9.0.0), a practice added in a "Pin GitHub Actions to commit SHAs" commit and kept current by Renovate.[^mz-linter]

## Rule files and editor setup

| File | Effect |
| --- | --- |
| `.markdownlint.yml` | list marker style `dash`; rules MD013 (line length), MD025, MD026, MD033, MD034, MD037, MD041 disabled[^mz-lintcfg] |
| `.yaml-lint.yml` | extends `default`; `document-start`, `line-length`, `new-line-at-end-of-file` disabled; `truthy` allows `true`, `false`, `on`[^mz-lintcfg] |
| `.hado-lint.yml` | ignores DL3008 (apt version pinning), although the benchmark Dockerfile has no `apt-get`, so the ignore is vestigial[^mz-lintcfg] |
| `.editorconfig` | LF, UTF-8, trimmed trailing whitespace, final newline; shell files use tabs of width 4[^mz-lintcfg] |
| `.vscode/` | recommends markdownlint, editorconfig and Markdown All in One; markdownlint as formatter with format on save/paste[^mz-lintcfg] |

## Renovate

Schedule "after 10pm and before 5am on weekdays, and weekends" in Europe/Stockholm, `config:recommended`, label `dependencies`, automerge of minor, patch, pin and digest updates, 7-day minimum release age, dependency dashboard, security label for vulnerability alerts. **The `dockerfile` manager is disabled**, so SDK base images in `larod-test` and `accuracy-test` are not bumped automatically; this is why the benchmark app still builds on SDK `12.0.0` while the table says AXIS OS 12.11.72.[^mz-renovate]

## Contribution rules

`CONTRIBUTING.md` asks for: bug reports with device model, firmware version, stack trace, OS and tool versions and reproduction steps; enhancement requests as issues; code contributions via fork, branch, **conventional commits** and pull request. Pull requests must build locally, pass all linters, match the existing style and carry explanatory comments. Local lint is run with a `github/super-linter:slim-v4` container (`RUN_LOCAL=true`), or with `hadolint`, `markdownlint`, `yamllint --config-file .yaml-lint.yml`, `shellcheck`, `shfmt`.[^mz-contributing] Model additions follow the four-step checklist in the auto-test framework README (see [model files](axis-model-zoo-model-files-and-licensing.md)).[^mz-readme]

## Ownership

A single CODEOWNERS rule assigns the whole repository to `@AxisCommunications/axis-model-zoo-admins` (see [repository overview](axis-model-zoo-repository.md)).

## Drifts and defects found

| Finding | Locator |
| --- | --- |
| CI uses super-linter **v9.0.0**, while contributors are told to reproduce locally with **slim-v4**, so local results can differ from the PR gate | `linter.yml` vs `CONTRIBUTING.md` local-lint section |
| `.gitignore` entries `__pycache__/` and `*.pyc` start with a leading space (confirmed with `cat -A`), so by git's pattern rules they most likely match nothing; the `larod-test/build/*` and `super-linter.log` patterns are well formed (**Observed** spacing, **Synthesis** effect) | `.gitignore` lines 1–4[^mz-gitignore] |
| Dockerfile Renovate manager disabled, so SDK pins drift | `renovate.json` |
| Vestigial Hadolint ignore | `.hado-lint.yml` |
| Benchmark workflow permissions conflict with its push step | see [speed pipeline](axis-model-zoo-speed-benchmark-pipeline.md) |

## Relationships

- **Part of:** [Axis Model Zoo repository](axis-model-zoo-repository.md).
- **Governs:** the scripts in [speed pipeline](axis-model-zoo-speed-benchmark-pipeline.md) and [accuracy harness](axis-model-zoo-accuracy-test-harness.md).
- **Comparable practice in sibling repos:** [ACAP Native SDK examples contribution, lint and CI](acap-examples-contribution-lint-and-ci.md), [ACAP SDK tools CI](acap-sdk-tools-ci-and-maintenance.md).

[^mz-readme]: `README.md` §Speed measure (link to the auto-test-framework directory and its model-add process).
[^mz-linter]: `.github/workflows/linter.yml` — `on`, `permissions`, checkout step, super-linter step `env` block.
[^mz-renovate]: `renovate.json` — `schedule`, `extends`, `labels`, `packageRules` (automerge, `matchManagers: ["dockerfile"]` disabled), `minimumReleaseAge`, `dependencyDashboard`.
[^mz-contributing]: `CONTRIBUTING.md` — bug report, enhancement, code contribution and local-lint sections.
[^mz-lintcfg]: `.markdownlint.yml`, `.yaml-lint.yml`, `.hado-lint.yml`, `.editorconfig`, `.vscode/extensions.json`, `.vscode/settings.json`.
[^mz-gitignore]: `.gitignore` lines 1–4.
