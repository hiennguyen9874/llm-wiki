---
type: Concept
title: "ACAP SDK tools: contribution rules, CI workflows, lint configuration and maintenance"
description: "How the acap-sdk-tools repository is contributed to and checked at git 7250746: the CONTRIBUTING gates, the super-linter workflow, two Docker build workflows, a stale example-checks workflow, lint and editor configuration, Renovate settings, and the mismatches between documented and actual checks."
tags: [edge-ai, axis, acap, ci, github-actions, super-linter, renovate, contributing]
status: stable
created: 2026-10-27
generated: { by: llm-wiki-agent/1, at: 2026-10-27T22:00:00Z }
stale_after: 2027-08-31
sources:
  - id: sdk-tools-readme
    resource: ../raw/acap-sdk-tools/README.md
    scope: ../raw/acap-sdk-tools/
    kind: code
    revision: "7250746d39fb25384402d0f900eb5a6a27c29d69 (2026-08-18)"
    title: "AxisCommunications/acap-sdk-tools — root README (git submodule)"
  - id: ci-contributing
    resource: ../raw/acap-sdk-tools/CONTRIBUTING.md
    scope: ../raw/acap-sdk-tools/
    kind: docs
    revision: "7250746"
    title: "CONTRIBUTING.md"
  - id: ci-linter
    resource: ../raw/acap-sdk-tools/.github/workflows/linter.yml
    scope: ../raw/acap-sdk-tools/
    kind: code
    revision: "7250746"
    title: "Workflow: Lint codebase"
  - id: ci-build-calibration
    resource: ../raw/acap-sdk-tools/.github/workflows/camera-calibration-for-lens-distortion.yml
    scope: ../raw/acap-sdk-tools/
    kind: code
    revision: "7250746"
    title: "Workflow: Build camera-calibration-for-lens-distortion tool"
  - id: ci-build-aws
    resource: ../raw/acap-sdk-tools/.github/workflows/train-tensorflow-model-using-aws.yml
    scope: ../raw/acap-sdk-tools/
    kind: code
    revision: "7250746"
    title: "Workflow: Build train-tensorflow-model-using-aws tool"
  - id: ci-example-checks
    resource: ../raw/acap-sdk-tools/.github/workflows/example-checks.yml
    scope: ../raw/acap-sdk-tools/
    kind: code
    revision: "7250746"
    title: "Workflow: Example repository checks"
  - id: ci-renovate
    resource: ../raw/acap-sdk-tools/.github/renovate.json
    scope: ../raw/acap-sdk-tools/
    kind: code
    revision: "7250746"
    title: "Renovate configuration"
  - id: ci-lint-config
    resource: ../raw/acap-sdk-tools/.markdownlint.yml
    scope: ../raw/acap-sdk-tools/
    kind: code
    revision: "7250746"
    title: "Lint and editor configuration (.markdownlint.yml, .yaml-lint.yml, .hado-lint.yml, .editorconfig, .vscode/)"
---

# ACAP SDK tools: contribution rules, CI workflows, lint configuration and maintenance

The [acap-sdk-tools repository](acap-sdk-tools-repository.md) is maintained with a standard Axis open-source setup: fork-and-PR contributions under conventional commits, a repository-wide super-linter run, one Docker-build smoke test per tool, and Renovate. This page records what those files actually do, because several of them no longer match the documentation or the repository layout. Everything is **Observed** by static reading of the files at revision 7250746 unless marked **Reported** or *Synthesis*; no workflow was run on GitHub.[^sdk-tools-readme]

## Contribution rules (Reported)

`CONTRIBUTING.md` asks contributors to fork, clone, create a branch with `git switch -c`, commit in [conventional commits](https://www.conventionalcommits.org) style, push and open a PR. Its PR checklist requires that the sample builds locally, all linters pass, commit messages follow the style, the change meets the existing sample standard, functions carry explanatory comments, and "no PR will be accepted without a well defined README". Bugs and enhancements go through GitHub Issues, with device model, firmware, stack trace and toolchain versions requested. It documents a local super-linter Docker run with the three lint configuration files. No branch-protection, release or versioning policy is documented.[^ci-contributing]

## Workflows

| Workflow | Trigger | What it does |
| --- | --- | --- |
| `linter.yml` — "Lint codebase" | `push` (any branch), `pull_request`, `workflow_dispatch`; `contents: read` | `actions/checkout` (v3.7.0, SHA-pinned, full history) then `super-linter/super-linter/slim` v5.7.2 (SHA-pinned) with `VALIDATE_ALL_CODEBASE`, `DEFAULT_BRANCH: main` and validators for Bash, Dockerfile (hadolint), Markdown, shfmt and YAML[^ci-linter] |
| `camera-calibration-for-lens-distortion.yml` — "Build … tool" | `push` with `paths: '**'` minus `.github/workflows/example-checks.yml`, `README.md`, `LICENSE`; no branch filter; no `pull_request` | Checks out (v2.8.0, SHA-pinned), runs `docker run --rm --privileged multiarch/qemu-user-static --credential yes --persistent yes` to register QEMU, then `cd $EXNAME; docker build --no-cache --tag acap-sdk-tools_$EXNAME:1.0 .` and removes the image[^ci-build-calibration] |
| `train-tensorflow-model-using-aws.yml` | identical to the above | Same steps with `EXNAME: train-tensorflow-model-using-aws`; a diff shows only the three name lines differ[^ci-build-aws] |
| `example-checks.yml` — "Example repository checks" | `push`/`pull_request` on `branches: [master]` | One shell step that requires every top-level directory to have an alphabetically ordered `* [name]` bullet in the README above a `## Docker Hub images` heading[^ci-example-checks] |

The build workflows only prove that each Docker image *builds*: nothing runs the calibration binary or the playbook, and the AWS image's `CMD` problem described in [the AWS training tool](acap-sdk-tools-aws-training-tool.md) would not be caught.

## Configuration files

- **Markdown:** `.markdownlint.yml` disables MD013 (line length), MD025 (multiple H1) and MD041 (first-line H1).
- **YAML:** `.yaml-lint.yml` extends `default` with `document-start`, `line-length` and `new-line-at-end-of-file` disabled and `truthy` allowing `'true'`, `'false'`, `'on'`.
- **Dockerfile:** `.hado-lint.yml` ignores DL3008 (apt package version pinning).
- **Editor:** `.editorconfig` sets LF, UTF-8, trimmed trailing whitespace; for `*.sh` it sets space indentation of 2 (its comment says "Tab indentation"). `.vscode/` recommends the markdownlint and EditorConfig extensions and makes markdownlint the Markdown formatter on save and paste.[^ci-lint-config]

## Renovate

`.github/renovate.json` extends `config:best-practices` and `:prHourlyLimitNone`, labels PRs `dependencies`, auto-merges minor and patch updates for dependencies whose current version does not start with `0`, requires a 14-day `minimumReleaseAge` for all update types, rebases when behind the base branch, labels vulnerability alerts `security`, creates PRs only once checks are not pending, and enables the dependency dashboard.[^ci-renovate] The three newest commits (2026-08-18) add this file, SHA-pin the actions and set read-only workflow token permissions; before that the last change was in May 2023 (11 commits in total) — evidence that the repository is in low-activity maintenance rather than active development. (*Synthesis* from git history; git metadata is not a declared file source.)

## Ownership and licence

`CODEOWNERS` assigns every path to `@AxisCommunications/acap-sdk-tools-owners`; the licence is Apache 2.0 and `CODE_OF_CONDUCT.md` is a Contributor Covenant text.[^sdk-tools-readme]

## Mismatches between documents and automation

1. `example-checks.yml` is stale: it triggers on `master` while the repository's default branch is `main`, and it looks for a `## Docker Hub images` heading that the README does not have (the README lists tools under `## Tools` with `- [` bullets). With an empty `endline` its `sed` range is invalid, so the step would fail if it ever ran (*Synthesis*).
2. The build workflows' `paths: '**'` makes every push (except edits to three files) build both tools, although their names suggest per-tool scoping.
3. Builds do not run on `pull_request`, while CONTRIBUTING makes "the sample code builds" a PR requirement; only the lint workflow covers PRs.
4. `CONTRIBUTING.md` documents the old `github/super-linter:slim-v4` image and URL; CI uses `super-linter/super-linter/slim` v5.7.2.
5. Action versions are uneven: checkout v3.7.0 in the lint workflow, v2.8.0 in the other three, both older than what the Renovate setup would propose.
6. `multiarch/qemu-user-static` is run unpinned although the actions were SHA-pinned in the same maintenance round.
7. The lint rule sets silence many default checks (line length, first-line H1, apt pinning, YAML document start), so "all linters pass" is a weaker gate than the CONTRIBUTING wording suggests. (*Synthesis*)

## Relationships

- **Maintains** both tools: [camera-calibration-for-lens-distortion](acap-sdk-tools-camera-calibration-tool.md) and [train-tensorflow-model-using-aws](acap-sdk-tools-aws-training-tool.md).
- **Part of** [ACAP SDK tools repository](acap-sdk-tools-repository.md).
- **Similar to** the push-only build checks and SHA-pinned actions of [ACAP Native SDK examples CI](acap-examples-contribution-lint-and-ci.md), [ACAP Runtime CI](acap-runtime-ci-and-maintenance.md) and [CV SDK examples CI](acap-cv-examples-ci-and-maintenance.md); the lint and build workflows here appear to follow the same Axis template. (*Synthesis*)

## Coverage and limits

Inspected: CONTRIBUTING.md, all four workflows, `renovate.json`, `CODEOWNERS`, `.editorconfig`, `.gitignore` (ignores `.DS_Store` and `*.log`), the three lint configurations and `.vscode/`. `CODE_OF_CONDUCT.md` and `LICENSE` were identified, not interpreted. Actual workflow run history, branch protection, open Renovate branches and the contents of the upstream actions are not local.

[^sdk-tools-readme]: Root README, §Tools, §How to work with GitHub repository, §License; `CODEOWNERS` line 1; `LICENSE` header; `CODE_OF_CONDUCT.md` title.
[^ci-contributing]: `CONTRIBUTING.md` §Reporting bugs, §Suggesting enhancements, §Code contribution (PR guidelines list), §Lint of code base.
[^ci-linter]: `.github/workflows/linter.yml`, keys `on`, `permissions`, `jobs.lint.steps[*].uses` and `env`.
[^ci-build-calibration]: `.github/workflows/camera-calibration-for-lens-distortion.yml`, keys `on.push.paths`, `env.EXNAME`, steps "qemu cross compiler" and "Build … application".
[^ci-build-aws]: `.github/workflows/train-tensorflow-model-using-aws.yml`; differs from the calibration workflow only at `name`, `env.EXNAME` and the build step name.
[^ci-example-checks]: `.github/workflows/example-checks.yml`, keys `on.*.branches` and the step "Verify that all examples have an entry in top-README" (`sed -n '/## Docker Hub images/='`).
[^ci-renovate]: `.github/renovate.json`, keys `extends`, `packageRules[0..1]`, `minimumReleaseAge`, `rebaseWhen`, `vulnerabilityAlerts`, `prCreation`, `dependencyDashboard`.
[^ci-lint-config]: `.markdownlint.yml` (MD013, MD025, MD041); `.yaml-lint.yml` (`extends`, `rules`); `.hado-lint.yml::ignored`; `.editorconfig` sections `[*]` and `[{*.sh}]`; `.vscode/extensions.json::recommendations`, `.vscode/settings.json`.
