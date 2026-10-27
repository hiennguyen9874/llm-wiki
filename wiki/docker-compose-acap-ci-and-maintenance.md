---
type: Concept
title: "Docker Compose ACAP CI, signing, release and maintenance"
description: "How docker-compose-acap builds, signs and pre-releases EAP files in GitHub Actions, its super-linter and cherry-pick workflows, Renovate scope, CONTRIBUTING rules, tag history and the stale or inconsistent maintenance items found at 4.0.0-2-g985c8ce."
tags: [edge-ai, axis, acap, docker, ci, github-actions, signing, renovate, release]
status: stable
created: 2026-10-27
generated: { by: llm-wiki-agent/1, at: 2026-10-27T22:00:00Z }
stale_after: 2027-04-30
sources:
  - id: dc-cd
    resource: ../raw/docker-compose-acap/.github/workflows/cd.yml
    scope: ../raw/docker-compose-acap/
    kind: code
    revision: "4.0.0-2-g985c8ce (985c8cede8b73d3a02a74c36e8a71d17b04852fe)"
    title: "cd.yml — Sign and prerelease"
  - id: dc-lint
    resource: ../raw/docker-compose-acap/.github/workflows/lint.yml
    scope: ../raw/docker-compose-acap/
    kind: code
    revision: "4.0.0-2-g985c8ce"
    title: "lint.yml — super-linter"
  - id: dc-cherry
    resource: ../raw/docker-compose-acap/.github/workflows/cherry-picker.yml
    scope: ../raw/docker-compose-acap/
    kind: code
    revision: "4.0.0-2-g985c8ce"
    title: "cherry-picker.yml"
  - id: dc-actions
    resource: ../raw/docker-compose-acap/.github/actions/metadata-action/action.yml
    scope: ../raw/docker-compose-acap/
    kind: code
    revision: "4.0.0-2-g985c8ce"
    title: "Composite actions: metadata, update-acap-manifest, docker-build"
  - id: dc-renovate
    resource: ../raw/docker-compose-acap/.github/renovate.json
    scope: ../raw/docker-compose-acap/
    kind: code
    revision: "4.0.0-2-g985c8ce"
    title: "Renovate configuration"
  - id: dc-contributing
    resource: ../raw/docker-compose-acap/CONTRIBUTING.md
    scope: ../raw/docker-compose-acap/
    kind: code
    revision: "4.0.0-2-g985c8ce"
    title: "CONTRIBUTING.md"
  - id: dc-meta
    resource: ../raw/docker-compose-acap/CODEOWNERS
    scope: ../raw/docker-compose-acap/
    kind: code
    revision: "4.0.0-2-g985c8ce"
    title: "CODEOWNERS and lint configuration"
---

# Docker Compose ACAP CI, signing, release and maintenance

Three GitHub Actions workflows maintain the repository: `cd.yml` builds both architectures, signs the EAP through the ACAP Service Portal and publishes a **prerelease** on tags; `lint.yml` runs super-linter; `cherry-picker.yml` pulls changes from the sibling `docker-acap` repository by hand. Renovate tracks only what its default managers detect, so most Docker-related version bumps are manual.[^dc-cd][^dc-lint][^dc-cherry][^dc-renovate] The build itself is in [Build and packaging](docker-compose-acap-build-and-packaging.md).

## `cd.yml`: sign and prerelease

- **Triggers:** push to `main`, push of semver-like tags (`X.Y.Z`, with `-rc.N`-style or dated suffixes), and pull requests to `main`; the two `!` patterns meant to exclude zero-prefixed suffixes are not supported by Actions tag globs and do nothing. Global permissions are `contents: read`.[^dc-cd]
- **Jobs:** `build`, `sign-eap`, `create_prerelease`, `download-and-upload-artifacts`, each with the matrix `arch: [armv7hf, aarch64]`; signing runs with `max-parallel: 1`.[^dc-cd]
- **Version:** the metadata action runs `docker/metadata-action` with semver patterns and an `-<arch>` suffix; a tag gives the exact version, a push to `main` gives `-<7-char SHA>` appended to the manifest version, so `main` builds look like `4.0.0-abc1234`. The `update-acap-manifest-action` writes the result into `app/manifest.json` at `.acapPackageConf.setup.version` with `jq`.[^dc-cd][^dc-actions]
- **Build:** the docker-build composite uses buildx and QEMU with `push: false` and `load: true`, outputs files locally, and hands the EAP to later jobs through a cache directory.[^dc-actions]
- **Signing:** a `curl POST` to `<ACAP_PORTAL_URL>/<signing id>/sign/binary` with a bearer token, expecting HTTP 200. Secrets named in the workflow are `ACAP_PORTAL_SIGNING_BEARER_TOKEN` and `ACAP_PORTAL_SIGNING_ID`, the variable is `ACAP_PORTAL_URL`, and the repository token is also used; no values are in the repository. This is the automated counterpart of the manual flow in [ACAP application signing](acap-application-signing.md).[^dc-cd]
- **Release:** only the tag path creates a GitHub release, always with `prerelease: true` and generated notes, then uploads signed EAPs by `curl` to the uploads endpoint expecting HTTP 201. Nothing in CI promotes a prerelease to a full release, so that step is manual.[^dc-cd]

## Lint and cherry-pick

`lint.yml` runs on push, pull request and manual dispatch using `super-linter/super-linter/slim` v9.0.0 with `VALIDATE_ALL_CODEBASE: true` and linters for Bash, clang-format, hadolint, Markdown, shfmt and YAML. `cherry-picker.yml` is `workflow_dispatch` only; it creates a `cherrybot-<random>` branch cherry-picking the tip of `AxisCommunications/docker-acap` and opens a pull request, retrying with `-X theirs` and prefixing the title `CHERRY-PICK CONFLICT` on failure.[^dc-lint][^dc-cherry]

## Renovate and ownership

Renovate extends `config:best-practices`, labels PRs `dependencies`, auto-merges minor and patch updates for versions not starting with 0, imposes a 14-day minimum release age and keeps a dependency dashboard. It defines **no custom managers**, so Dockerfile `ARG` versions (Docker, Compose, SDK, procps, util-linux, slirp4netns) are not tracked. All `CODEOWNERS` lines resolve to `@AxisCommunications/docker-acap-owners` and `@AxisCommunications/docker-acap-reviewers`.[^dc-renovate][^dc-meta] The markdownlint config sets 100-column lines (code blocks exempt) and disables MD025, MD033 and MD041; yamllint extends `default` with three rules off.[^dc-meta]

## Contribution rules

`CONTRIBUTING.md` covers questions, bug reports, enhancement suggestions and a first-contribution path: fork, branch, Conventional Commits, push and PR, with a locally building change that passes linters. It states that changes under `.github` are not accepted from contributors, and documents no release process.[^dc-contributing]

## History

204 commits from 2021-07-06 to 2026-10-21 and 33 local tags from `1.1.1` onward to `4.0.0`; the scheme is `X.Y.Z` with `-rc.N` or `-preview.N` suffixes pushed by hand. Two release lines interleave: `1.5.0` (AXIS OS 2022 LTS) was cut after `2.0.0-preview.*`, and `2.0.1-preview.1` was never released. The Native SDK moved from 3.4 (2021) through 1.x tags to 12.0.0 on 2026-10-14; Compose went from v2.18.1 to v2.25.0 to v5.5.0; Engine from 26.0.0 to 29.8.1, with procps, util-linux and slirp4netns bumped the same day.[^dc-cd][^dc-meta]

## Stale or inconsistent items (Observed)

1. `cherry-picker.yml` declares `contents: read` yet pushes a branch and opens a PR.
2. `CONTRIBUTING.md` documents super-linter `slim-v8` and a local linter set without clang-format, while the workflow runs v9 with clang-format.
3. `lint.yml` always validates the whole codebase, not the PR diff.
4. The manifest's `embeddedSdkVersion` is 3.0 against SDK 12.0.0, and `build.sh` carries a stale default tag.
5. The signed EAP depends on three repository-level secrets and variables that are not reproducible by a fork.
6. Minor: a typo in the metadata-action input description and a hard-coded Docker context `.`.[^dc-cd][^dc-actions][^dc-contributing]

## Evidence class

Workflow structure and inconsistencies are **Observed** by static reading; no workflow ran, no secret was read, and no signing request was made. History comes from the local git checkout (**Observed**); the existence of a corresponding GitHub release for each tag was not checked.

## Relationships

- **Part of** [Docker Compose ACAP repository](docker-compose-acap-repository.md).
- **Builds** the artifact described in [Build and packaging](docker-compose-acap-build-and-packaging.md).
- **Mirrors** the push-only, SHA-pinned CI pattern in [ACAP Native SDK repository CI](acap-native-sdk-repo-ci-and-maintenance.md) and the examples workflows in [ACAP examples contribution, lint and CI](acap-examples-contribution-lint-and-ci.md), but adds signing and prerelease creation; Renovate scope differs from those repositories.
- **Related to** the sibling `docker-acap` repository only through the cherry-pick workflow; that repository is not local.

[^dc-cd]: `.github/workflows/cd.yml::{on, permissions, jobs.build, jobs.sign-eap, jobs.create_prerelease, jobs.download-and-upload-artifacts}`; git: `git log`, `git tag`, `git rev-list --count HEAD`.
[^dc-lint]: `.github/workflows/lint.yml::{on, jobs.lint}`.
[^dc-cherry]: `.github/workflows/cherry-picker.yml::{on, permissions, steps}`.
[^dc-actions]: `.github/actions/metadata-action/action.yml`, `.github/actions/update-acap-manifest-action/action.yml`, `.github/actions/docker-build-action/action.yml` (inputs, `docker/metadata-action` tags and flavor, `jq` update of `.acapPackageConf.setup.version`, build step).
[^dc-renovate]: `.github/renovate.json::{extends, packageRules, minimumReleaseAge, dependencyDashboard}`.
[^dc-contributing]: `CONTRIBUTING.md` §I have a question, §I want to contribute (Reporting bugs, Suggesting enhancements, Your first code contribution incl. the `.github` note), §Lint of codebase (Linters in GitHub Action, Run super-linter locally).
[^dc-meta]: `CODEOWNERS` line 1; `.markdownlint.yaml`; `.yamllint.yml`; `git log --format` over `Dockerfile` for version history.
