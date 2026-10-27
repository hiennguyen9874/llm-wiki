---
type: Concept
title: "CI and maintenance of the ACAP 3 SDK repository"
description: "What acap3-sdk verifies and automates: a push-only, path-filtered build check of both Dockerfiles with SHA-pinned actions and a read-only token, no image publishing, Renovate limited to Actions bumps with automerge, and one catch-all code owner."
tags: [edge-ai, axis, acap, sdk-3, ci, github-actions, renovate, maintenance]
status: stable
created: 2026-10-27
generated: { by: llm-wiki-agent/1, at: 2026-10-27T19:00:00Z }
stale_after: 2027-04-30
sources:
  - id: acap3-sdk-repo
    resource: ../raw/acap3-sdk/README.md
    scope: ../raw/acap3-sdk/
    kind: code
    revision: "3.5-aarch64-28-g4e4fe04 (4e4fe046e47dcbbfcdf6bd14b0473e90d8ce5e50, 2026-10-01)"
    title: "AxisCommunications/acap3-sdk (git checkout)"
---

# CI and maintenance of the ACAP 3 SDK repository

The only automation is a GitHub Actions workflow that checks that each Dockerfile still builds. It does not test the resulting SDK, does not publish an image and does not run on pull requests. Renovate is enabled but keeps only the GitHub Actions versions current, because its Dockerfile manager is disabled; base images and `protoc` are bumped by hand, if at all. Since the Dockerfiles have not changed since 2022-06-30, the 2026 history is almost entirely action bumps.[^acap3-sdk-repo] Context: [ACAP 3 SDK repository](acap3-sdk-repository.md), [image assembly](acap3-sdk-image-assembly.md).

Evidence class: **Observed** from `.github/workflows/build-dockerfile.yml` (25 lines), `.github/renovate.json` (22 lines), `CODEOWNERS` and `git log`. No workflow run was observed, so pass rates are **Unverified**.

## Workflow `Control Dockerfiles`

| Aspect | Value |
| --- | --- |
| Trigger | `push` only, filtered to `Dockerfile*` and `.github/workflows/build-dockerfile.yml`; no `pull_request`, `schedule`, `workflow_dispatch` or tag trigger |
| Permissions | `contents: read` (added 2026-08-18, PR #53) |
| Job | One job `build` on `ubuntu-latest` |
| Matrix | `arch: ["armv7hf", "aarch64"]`, building `Dockerfile.${{ matrix.arch }}` |
| Steps | `actions/checkout` v7.0.1, `docker/setup-buildx-action` v4.4.1, `docker/build-push-action` v7.4.0, each pinned to a full commit SHA with the version in a trailing comment (PR #54) |
| Output | `push: false`, no `tags`, no registry login, no secrets: nothing is published |

**Synthesis:** because the trigger is push-only and path-filtered, a pull request that edits a Dockerfile is not built before merge; the check runs only after a push to a branch. Rebuilding is also not scheduled, so a change in an upstream mutable input (`axisecp/acap-*:3.5-*` tags, the Maven `protoc` URL, the Khronos `master` file; see [image assembly](acap3-sdk-image-assembly.md)) goes unnoticed until someone edits a Dockerfile.[^acap3-sdk-repo]

## Renovate

- Extends `config:base` and `:prHourlyLimitNone`; schedule "after 10pm and before 5am every weekday" plus weekends; `labels: ["dependencies"]`; `rebaseWhen: behind-base-branch`; `stabilityDays: 7`; `prCreation: not-pending`; `dependencyDashboard: true`; vulnerability alerts labeled `security`.
- Package rules: `minor`, `patch`, `pin` and `digest` updates are **automerged**; major updates are not. The `dockerfile` manager is **disabled**, so only Actions in the workflow are tracked.
- Observed effect in history: Renovate PRs raised `actions/checkout` 4 → 6 → 7, `docker/build-push-action` 4 → 7.4.0 and `docker/setup-buildx-action` 3 → 4.4.1 between 2023 and 2026. The last human-authored commits are the two 2026-08-18 hardening changes.
- Contrast: [the Native SDK repository](acap-native-sdk-repo-ci-and-maintenance.md) has the same workflow and hardening commits but disabled Renovate entirely.

## Ownership and contribution

`CODEOWNERS` has one rule, `* @AxisCommunications/acap3-sdk-owners`. The repository has no `CONTRIBUTING`, security policy, issue or pull-request templates, or CodeQL/dependabot configuration (the whole `.github` tree is the two files above). Commit `ac16b53` (2022-04-27) added the code owners.[^acap3-sdk-repo]

## Limits

- Team membership, branch protection, whether the build check is a required status and whether Renovate runs as a hosted app or self-hosted are not visible from the files.
- The 2026 commit dates and action versions are as recorded in the local git history; they were not compared with upstream releases.

## Relationships

- **Part of** [ACAP 3 SDK repository](acap3-sdk-repository.md); **checks** [image assembly](acap3-sdk-image-assembly.md).
- **Parallels** [CI and maintenance of the ACAP Native SDK repository](acap-native-sdk-repo-ci-and-maintenance.md) and the build-only workflows in [ACAP SDK tools CI](acap-sdk-tools-ci-and-maintenance.md); the shared push-only gap is also noted in [ACAP Native SDK examples CI](acap-examples-contribution-lint-and-ci.md).

[^acap3-sdk-repo]: [AxisCommunications/acap3-sdk](../raw/acap3-sdk/README.md) at `4e4fe04`: `.github/workflows/build-dockerfile.yml` lines 1-25 (name, `on.push.paths`, `permissions`, matrix, three `uses:` lines, `push: false`); `.github/renovate.json` (keys `schedule`, `extends`, `labels`, `packageRules`, `rebaseWhen`, `vulnerabilityAlerts`, `stabilityDays`, `prCreation`, `dependencyDashboard`); `CODEOWNERS` line 1; `git log` subjects `8a4b0b5`, `aacaf68`, `06f6ed1`, `ac16b53`, and the Renovate bump commits from 2023 to 2026.
