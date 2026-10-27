---
type: Concept
title: "CI and maintenance of the ACAP Native SDK repository"
description: "What the acap-native-sdk repository verifies and automates: a push-only build check of both Dockerfiles with SHA-pinned actions and read-only token, no image publishing, Renovate disabled, and a single catch-all code owner."
tags: [edge-ai, axis, acap, sdk, ci, github-actions, maintenance]
status: stable
created: 2026-10-27
generated: { by: llm-wiki-agent/1, at: 2026-10-27T18:00:00Z }
stale_after: 2027-04-30
sources:
  - id: acap-native-sdk-repo
    resource: ../raw/acap-native-sdk/README.md
    scope: ../raw/acap-native-sdk/
    kind: code
    revision: "12.10.0-2-geed6dcf (eed6dcff23c17e744b773473646251752b91184f, 2026-08-18)"
    title: "AxisCommunications/acap-native-sdk (git submodule)"
---

# CI and maintenance of the ACAP Native SDK repository

The repository's only automation is a GitHub Actions workflow that checks that each Dockerfile still builds. It does not test the resulting SDK, does not publish an image, and does not run on pull requests. Dependency automation (Renovate) is switched off. Both facts matter for anyone reasoning about how trustworthy or reproducible the published SDK image is, because the repository itself produces no artifact.[^acap-native-sdk-repo] Context: [ACAP Native SDK repository](acap-native-sdk-repository.md), [image assembly](acap-native-sdk-image-assembly.md).

Evidence class: **Observed** from `.github/workflows/build-dockerfile.yml` (25 lines), `.github/renovate.json` (3 lines), `CODEOWNERS` and commit diffs. No workflow run was observed, so actual pass rates and runner behavior are **Unverified**.

## Workflow `Control Dockerfiles`

| Aspect | Value |
| --- | --- |
| Trigger | `push` only, with path filters `Dockerfile*` and `.github/workflows/build-dockerfile.yml`; no `pull_request`, `schedule` or `workflow_dispatch` |
| Permissions | `contents: read` at workflow level (added by `6ee96ae`, #88) |
| Job | `build` on `ubuntu-latest`, matrix `arch: ["armv7hf", "aarch64"]` |
| Steps | checkout, `docker/setup-buildx-action`, `docker/build-push-action` with `file: "Dockerfile.${{ matrix.arch }}"` and `push: false` |
| Registry, image name, tags, cache | none; the built image is discarded |
| Secrets | none referenced |

Action pins (by `eed6dcf`, #89), each a full 40-character commit SHA with a version comment: `actions/checkout` v6.1.0 (`d23441a4...`), `docker/setup-buildx-action` v3.12.0 (`8d2750c6...`), `docker/build-push-action` v6.19.2 (`10e90e36...`).[^acap-native-sdk-repo]

### Consequences (Synthesis)

- The check proves only that `docker build` succeeds with the default build args (`latest` builder images, `AXIS_OS_VERSION_TAG=unknown`, no `--build-arg`). It does not exercise `acap-build`, the environment script or any application, and it cannot catch a runtime regression in the toolchain.
- Because there is no `pull_request` trigger, a change proposed in a PR is not built before merge by this workflow; it is built on the `push` that follows. Whether branch protection or a different workflow compensates is not visible in the repo.
- Because `latest` base images are pulled on every run, a green run reflects the state of the upstream images that day, not a fixed environment.
- The published `axisecp/acap-native-sdk` images are produced elsewhere (**Unverified**: no publishing logic is present here), so release procedure, signing and scanning of those images are outside this evidence.

## Dependency automation

`.github/renovate.json` is the whole object `{ "enabled": false }`. `0423873` (#84, 2026-02-10) replaced a 22-line config with it. The removed config had a night/weekend schedule, `config:base`, automerge for minor/patch/pin/digest updates, a 7-day stability window, a dependency dashboard, a security label for vulnerability alerts, and a `packageRules` entry that already disabled the `dockerfile` manager.[^acap-native-sdk-repo] **Observed:** even before the kill switch the `dockerfile` manager was disabled and no custom regex manager existed, so Renovate did not track the Dockerfile `FROM` or `ARG` versions. **Synthesis:** it could therefore only have updated GitHub Actions, as in commit `2baaefe` "Update the checkout action ... (renovate)". With Renovate off, action pins in the workflow are now updated by hand, and the SHA pinning in #89 makes silent upstream tag moves impossible but also freezes versions until someone bumps them.

## Ownership

`CODEOWNERS` has one rule, `* @AxisCommunications/acap-native-sdk-owners`: a single team owns every file and there are no path-specific reviewers.

## Maintenance guidance for readers (Synthesis)

- To judge freshness of the SDK image, look at `git describe` and the list-edit commits, not at CI: CI is build-only and `latest`-based.
- Hard-coded values likely to drift: `ubuntu:24.04` (both Ubuntu args), the `khrplatform.h` URL on a floating branch, the glob-based removal lists and the `eap-install.sh` package comment. This is why the owning concepts carry `stale_after`.
- No test, linter (for example `hadolint`), vulnerability scanner or image-size check exists in this repo.

## Relationships

- **Part of** [ACAP Native SDK repository](acap-native-sdk-repository.md).
- **Verifies** the build of [SDK image assembly](acap-native-sdk-image-assembly.md) and [sysroot pruning](acap-native-sdk-sysroot-pruning.md).
- **Compare with** [CI, maintenance and staleness of the CV SDK examples repository](acap-cv-examples-ci-and-maintenance.md), the sibling repository whose CI and CODEOWNERS were also compiled.

[^acap-native-sdk-repo]: [AxisCommunications/acap-native-sdk](../raw/acap-native-sdk/README.md) at `eed6dcf`: `.github/workflows/build-dockerfile.yml` lines 1-25; `.github/renovate.json` lines 1-3; `CODEOWNERS` line 1; `git show` of `0423873`, `6ee96ae`, `eed6dcf`, `2baaefe`.
