---
type: Concept
title: "ACAP Runtime CI/CD, linting, contribution rules and stale items"
description: "What the acap-runtime workflows, composite actions, Renovate config, lint files and CONTRIBUTING actually do: the build-test-containerize-prerelease pipeline, image tag scheme, secret names, supply-chain hardening, release history, and the broken or stale items found."
tags: [edge-ai, axis, acap, acap-runtime, ci, github-actions, renovate, lint, maintenance]
status: stable
created: 2026-10-27
generated: { by: llm-wiki-agent/1, at: 2026-10-27T21:00:00Z }
stale_after: 2027-08-31
sources:
  - id: rt-readme
    resource: ../raw/acap-runtime/README.md
    scope: ../raw/acap-runtime/
    kind: code
    revision: "2.0.1-10-ge375fc9 (e375fc9586e270042c9c46dde7645c20761b06bf)"
    title: "ACAP Runtime README (release table, badges)"
  - id: rt-cicd
    resource: ../raw/acap-runtime/.github/workflows/ci-cd.yml
    scope: ../raw/acap-runtime/
    kind: code
    revision: "2.0.1-10-ge375fc9"
    title: "ci-cd.yml — build, test, containerize, prerelease"
  - id: rt-lint
    resource: ../raw/acap-runtime/.github/workflows/lint.yml
    scope: ../raw/acap-runtime/
    kind: code
    revision: "2.0.1-10-ge375fc9"
    title: "lint.yml — super-linter"
  - id: rt-actions
    resource: ../raw/acap-runtime/.github/actions/docker-build-push-action/action.yml
    scope: ../raw/acap-runtime/
    kind: code
    revision: "2.0.1-10-ge375fc9"
    title: "composite actions (docker-build-push, metadata, pytest, update-acap-manifest)"
  - id: rt-renovate
    resource: ../raw/acap-runtime/.github/renovate.json
    scope: ../raw/acap-runtime/
    kind: code
    revision: "2.0.1-10-ge375fc9"
    title: "renovate.json"
  - id: rt-contributing
    resource: ../raw/acap-runtime/CONTRIBUTING.md
    scope: ../raw/acap-runtime/
    kind: code
    revision: "2.0.1-10-ge375fc9"
    title: "CONTRIBUTING.md"
---

# ACAP Runtime CI/CD, linting, contribution rules and stale items

The repository's automation is three workflows and four local composite actions. The pipeline builds a **test image and a containerized image per architecture**, runs the test suite on **real cameras**, and creates a GitHub pre-release on a version tag; a separate workflow publishes the protofiles image, and super-linter checks style. Supply-chain hardening (SHA-pinned actions, read-only tokens, Renovate) was added after 2.0.1 but is only partly applied. The workflows were read statically, never executed.[^rt-cicd][^rt-lint]

## `ci-cd.yml`

- **Triggers:** push to `main` and to semver tags (plain, `-<prerelease>.<n>` and `-<date>` forms); pull requests to `main`, ignoring markdown, `CODEOWNERS`, `LICENSE`, config dotfiles and `.vscode/*`.
- **Jobs:** `general_settings` → in parallel `build_and_test` and `build_containerized` (matrix `arch: [armv7hf, aarch64]`) → `create_prerelease` (tags only). `general_settings` computes `EVENT_TYPE`, `SHORT_SHA` and `BUILD_EAP` (hard-coded `false`), but nothing consumes them.
- **`build_and_test`:** builds target `runtime-base` with `TEST=true`, pushes `<repo>:<version>-<arch>-test` **unconditionally** (a commented-out guard leaves it pushed from same-repo PRs too), then runs `pytest -s ./.github/test/test_acapruntimetest.py` against devices behind a device-server proxy (`…/camera1` for armv7hf, `…/camera2` for aarch64) with `AXIS_EXTERNAL_POOL: true` ([Test suite](acap-runtime-test-suite.md)).
- **`build_containerized`:** builds and pushes `<repo>:<version>-<arch>-containerized`; push only when the event is not a pull request. It rewrites the manifests' version through `update-acap-manifest-action` (a `jq` edit of the checked-out workspace; nothing is committed back).
- **`create_prerelease`:** `actions/github-script` creates a release with `prerelease: true` and generated notes; its output is unused and **no job promotes it to a final release**, although the README links `releases/latest`.
- **Permissions:** workflow-level `contents: read`; `contents: write` only on the prerelease job.
- **Secret and variable names** (values not inspected): `DEVICE_SRVR_IP`, `DEVICE_USER`, `DEVICE_SRVR_PASS`, `ECOSYSTEM_SERVICE_USER_DOCKER_HUB`, `ECOSYSTEM_ACCESS_TOKEN_DOCKER_HUB`, `GITHUB_TOKEN`; variable `REPOSITORY_DOCKER_HUB`.

### Image tags and version

The version comes from the **git tag through `docker/metadata-action`** (semver patterns, branch and PR refs), not from `git describe` or the manifest. Results: `2.0.1-aarch64-containerized`, `2.0.1-armv7hf-test`, `main-<arch>-containerized` on main, `pr-<n>-…` on pull requests, and `<version>-protofiles` from `build-proto-image.yml`. Docker Hub (`docker.io`) is the default registry and login happens only when pushing.[^rt-actions]

## Lint and editor configuration

`lint.yml` runs on every push, pull request and manual dispatch: **super-linter slim v8.7.0** pinned by commit SHA, `VALIDATE_ALL_CODEBASE`, validating bash, clang-format, Dockerfile (hadolint), markdown, shfmt and YAML. Config files: `.markdownlint.yaml` (MD013/MD025/MD033/MD041 off), `.yamllint.yml`, `.hadolint.yaml` (ignores DL3003, DL3008, SC2103, SC2164), `.clang-format` (LLVM base, 100 columns, 4-space indent kept deliberately to limit diff size) and `.editorconfig`.[^rt-lint]

## Dependency management

Renovate extends `config:best-practices` and `:prHourlyLimitNone`, labels PRs `dependencies`, enforces a 14-day `minimumReleaseAge`, automerges minor and patch updates of non-`0.x` dependencies, enables the dashboard and labels vulnerability alerts `security`. Workflow files pin actions by SHA with version comments (`actions/checkout` v5.1.0, `github-script` v8.0.0, super-linter v8.7.0); the **composite actions still use floating tags** (`docker/build-push-action@v6`, `setup-buildx-action@v3`, `setup-qemu-action@v3`, `login-action@v3`, `metadata-action@v5`, `setup-python@v6`, `upload-artifact@v4`).[^rt-renovate][^rt-actions] This matches the hardening commits after 2.0.1 (SHA pinning, read-only token, Renovate added, dependabot dropped) in `git log`.

## Contribution rules

`CONTRIBUTING.md` asks contributors to fork and branch, use **conventional-commit** messages, build locally, pass all linters, match code style and comment code. It states that code changes under `.github/` "will not be accepted". It documents the CI flow (test image, device run, containerized image) and that forks need their own registry, secrets and device addresses, and gives local lint recipes with `ghcr.io/super-linter/super-linter:slim-v7`. It has no release-process section. `CODEOWNERS` is one catch-all line for two Axis teams (`acap-runtime-owners` and `docker-acap-reviewers`), with no separate ownership of `.github/`.[^rt-contributing]

## Stale or broken items (Observed)

1. `build_containerized` passes `RUNTIME_VERSION=${{ steps.meta.outputs.version }}` but the step id is `meta_containerized`, so the value is empty; the Dockerfile also never declares `RUNTIME_VERSION`.
2. README release table and examples are one release behind (`2.0.0` vs tag `2.0.1`), and README text about default chip ids 4/12 describes a native application that is no longer published ([Server configuration](acap-runtime-server-configuration-and-security.md)).
3. Manifests in the tree say `1.3.1`.
4. `paths-ignore` names `.yamllint.yaml` but the file is `.yamllint.yml`.
5. CONTRIBUTING mentions `slim-v7` and the older `github/super-linter` path; the workflow uses v8.7.0 and also enables `VALIDATE_CLANG_FORMAT`, which CONTRIBUTING's local recipe omits.
6. Tag patterns use unescaped dots and `[1-9]+`; the historical tag `v1.2.0-rc.1` (leading `v`) matches none.
7. The proto workflow hard-codes `axisecp/acap-runtime`, is arm64-only, and pushes on `success()` without a push-event guard.
8. Release history: `1.3.1` (2023-04-24) → `2.0.0` (2024-09-20) → `2.0.1` (2025-06-18); native-eap deployment was dropped between 1.3.1 and 2.0.0 (commit "Stop building and deploying eap"), with a later README note about the removed eap-file.[^rt-readme]

## Relationships

- **Tests with:** [Test suite](acap-runtime-test-suite.md); **builds with:** [Build and image packaging](acap-runtime-build-and-image-packaging.md).
- **Compare:** the sibling repositories' CI in [CV SDK examples CI](acap-cv-examples-ci-and-maintenance.md), [Native SDK CI](acap-native-sdk-repo-ci-and-maintenance.md) and [Native SDK examples CI](acap-examples-contribution-lint-and-ci.md); this one is distinctive for running tests on physical devices and pushing to Docker Hub.
- **Part of:** [ACAP Runtime repository](acap-runtime-repository.md).

## Evidence class

All items are **Observed** from the workflow files, actions, configs and `git log`; no workflow ran. The meaning of `vars.REPOSITORY_DOCKER_HUB` (presumably `axisecp/acap-runtime`) and the secret values are **Unverified** and were not inspected.

[^rt-readme]: `README.md` §Notable Releases and badges; `git tag --sort=-creatordate`, `git log --oneline` of the checkout (commits `f2d8d60`, `aca2cd1`, `12d3e45`, `3943c12`, `c52437f`, `f4a5d7a`, `1a8626e`, `dc6db0b`, `d280187`).
[^rt-cicd]: `.github/workflows/ci-cd.yml::{triggers L7-35, general_settings L41-65, build_and_test L67-136, build_containerized L138-179 (RUNTIME_VERSION L172), create_prerelease L181-210}`.
[^rt-lint]: `.github/workflows/lint.yml::{triggers L4-7, super-linter L22-34}`; `.markdownlint.yaml`, `.yamllint.yml`, `.hadolint.yaml` L2-5, `.clang-format` L20-23, `.editorconfig`.
[^rt-actions]: `.github/actions/docker-build-push-action/action.yml` L44-92; `.github/actions/metadata-action/action.yml` L44-66; `.github/actions/pytest-action/action.yml` L16-41; `.github/actions/update-acap-manifest-action/action.yml` L25-41.
[^rt-renovate]: `.github/renovate.json` L1-25.
[^rt-contributing]: `CONTRIBUTING.md` L151-153 (commit style), L164-170 (`.github` rule), L176-186 (CI flow and forks), L196-235 (lint recipes); `CODEOWNERS` L1.
