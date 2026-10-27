---
type: Concept
title: "CI, maintenance and known staleness of the CV SDK examples repository"
description: "What the acap-computer-vision-sdk-examples workflows, Renovate config, issue templates and lint files actually do, what they do not test, and the broken links, dead entries and build-argument mismatches found in the repository."
tags: [edge-ai, axis, acap, ci, github-actions, renovate, maintenance, examples]
status: stable
created: 2026-10-27
generated: { by: llm-wiki-agent/1, at: 2026-10-27T14:00:00Z }
stale_after: 2027-08-31
sources:
  - id: cvex-readme
    resource: ../raw/acap-computer-vision-sdk-examples/README.md
    scope: ../raw/acap-computer-vision-sdk-examples/
    kind: code
    revision: "12.10.0-3-g98b1ea7"
    title: "ACAP Computer Vision SDK examples — repository README"
  - id: cvex-ci
    resource: ../raw/acap-computer-vision-sdk-examples/.github/workflows/example-checks.yml
    scope: ../raw/acap-computer-vision-sdk-examples/
    kind: code
    revision: "12.10.0-3-g98b1ea7"
    title: "GitHub Actions workflows, Renovate config, issue templates and lint files"
---

# CI, maintenance and known staleness of the CV SDK examples repository

The [CV SDK examples repository](acap-cv-sdk-examples-repository.md) has a lightweight automation layer: one build workflow per example, a README-list checker, a one-way sync to a staging repository, Renovate for dependency updates, and issue templates that mainly collect model-debugging information. The automation checks that the images build and that the README catalog is complete and sorted; it does not run, lint or deploy anything. Because the repository is archived in practice (see the deprecation banner in the overview), the staleness items below matter when copying patterns from it.[^cvex-ci][^cvex-readme]

## Workflows

| Workflow | Trigger | What it does |
| --- | --- | --- |
| `<example>.yml` ×7 (`hello-world-python`, `minimal-ml-inference`, `object-detector-python`, `opencv-qr-decoder-python`, `parameter-api-python`, `pose-estimator-with-flask`, `web-server`) | `push` with path filter `<example>/**` (excluding that example's `README.md`) plus its workflow file; `pull_request` with **no** path filter | Registers qemu (`docker run --rm --privileged multiarch/qemu-user-static --credential yes --persistent yes`), then `docker build --no-cache --tag acap-computer-vision-examples_<NAME>:1.0 .` on `ubuntu-latest` |
| `example-checks.yml` | push and PR on `main` | Shell check that every top-level non-dot directory is listed in `README.md` as `* [name]` and that the list is sorted |
| `auto-sync-to-staging.yml` | push to `main`, manual dispatch | Clones `AxisCommunications/<repo>-staging` using the secret `API_TOKEN_GITHUB`, copies the workspace in (minus this workflow), commits as `ecosvc-dockerhub` to branch `Auto-sync-<date_time>` and pushes |

Findings (**Observed**):[^cvex-ci]

- Three examples (`minimal-ml-inference`, `object-detector-python`, `pose-estimator-with-flask`) use a build matrix `chip: [cpu, artpec8]` that adds `--build-arg CHIP=<chip>` and also builds `Dockerfile.model`. No Dockerfile declares a `CHIP` argument, so the two matrix legs build identical images; the real chip selection occurs at run time through `INFERENCE_CHIP` in the env files ([Runtime architecture](acap-cv-examples-runtime-architecture.md)).
- The jobs use `docker build` although `docker/setup-buildx-action` with `install: true` is configured; buildx is effectively unused.
- Actions are pinned by commit SHA with a version comment (`actions/checkout` v2.8.0, `docker/setup-buildx-action` v2.10.0; auto-sync uses checkout v3.7.0). All workflows set `permissions: contents: read`.
- There are no tests, no lint step, no compose validation and no device deployment. Passing CI means only that `docker build` succeeded.
- `auto-sync-to-staging.yml` decides "nothing to commit" by grepping `git commit` output without `pipefail`, which is fragile.
- Only one secret name appears: `API_TOKEN_GITHUB` (values not inspected).

## Dependency management

`.github/renovate.json` extends `config:best-practices` and `:prHourlyLimitNone`, labels PRs `dependencies`, auto-merges minor and patch updates for dependencies whose current version does not start with `0`, enforces a 14-day `minimumReleaseAge`, rebases when behind base, labels vulnerability alerts `security`, and enables the dependency dashboard.[^cvex-ci] This is the only mechanism that could advance the pinned `2.0.1` Runtime or `ubuntu:24.04` tags; the unpinned `apt`/`pip` packages and the `alpine:latest` model images are outside its reach.

## Issue templates

Both templates (`bug_report.md`, `issue-with-custom-model.md`) refuse security disclosures in issues and ask for a compatibility checklist. The custom-model template additionally requires the reporter to have followed minimum debug steps: run `larod-client -g model_path -c <CHIP_ID>` with channel IDs `cpu-tflite`, `axis-a8-dlpu-tflite` (ARTPEC-8 DLPU), `google-edge-tpu-tflite` (ARTPEC-7 TPU) or `ambarella-cvflow` (CV25 DLPU), and attach `journalctl -u larod` output.[^cvex-ci] It connects this container-era repository to the on-device model-checking procedure in [Triển khai custom AI model lên camera Axis](axis-custom-model-deployment.md) and to the DLPU families in [Axis DLPU](axis-dlpu.md).

## Lint and ownership

`.markdownlint.yml` disables `MD013` (line length) and `MD041` (first-line heading, because of the copyright header). `.editorconfig` requires spaces, LF endings, trimmed whitespace and a final newline. `.vscode/extensions.json` recommends markdownlint, EditorConfig and the code-spell-checker, whose word list contains `armv7hf` even though only `aarch64` is supported. No workflow runs markdownlint or EditorConfig checks. `CODEOWNERS` assigns everything to the team `@AxisCommunications/acap-computer-vision-sdk-owners` and two path overrides to an individual handle.[^cvex-ci]

## Stale or broken items

All **Observed** in the checkout:[^cvex-ci][^cvex-readme]

1. The README CI badge points to `ci.yml`, which no longer exists (removed in a workflow update); the badge is broken.
2. The README's "refactored" sentence links the new setup to this same repository.
3. The README says ACAP Runtime is used "in a few examples"; five of seven use it.
4. `CODEOWNERS` lists `/parameter-api-cpp` (a removed C++ example) and `/parameter-api-python`; `.gitignore` ignores `parameter-api/models`, a directory that does not exist.
5. Both issue templates link `../../SECURITY.md`, which is absent.
6. Checkout action versions differ between the build and sync workflows.
7. Example READMEs contradict their code in several places; those are recorded on the example pages ([ML](acap-cv-example-ml-inference-and-object-detection.md), [pose](acap-cv-example-pose-estimator-flask.md), [QR](acap-cv-example-opencv-qr-decoder.md), [Parameter API](acap-cv-example-parameter-api.md), [web server](acap-cv-example-monkey-web-server.md)).

## Relationships

- **Part of:** [ACAP Computer Vision SDK examples repository](acap-cv-sdk-examples-repository.md).
- **Interpretation (synthesis):** a green build here is weak evidence that an example works on a camera; use [build and deploy workflow](acap-cv-examples-build-deploy-workflow.md) for real verification.

## Source coverage

- Inspected: all 9 workflow files plus `.github/renovate.json`, both issue templates, `.markdownlint.yml`, `.editorconfig`, `.vscode/*`, `.gitignore`, `CODEOWNERS`. Git history was consulted only to date the removal of `ci.yml` and the C++ example; no workflow was run and no staging repository or secret was accessed.

## Evidence class

Workflow behavior and stale items are **Observed** by static reading; the weak-evidence statement is **Synthesis**. No run results were obtained.

[^cvex-readme]: `raw/acap-computer-vision-sdk-examples/README.md` §Note, §Required components, badge on line 3, at `12.10.0-3-g98b1ea7`.
[^cvex-ci]: `.github/workflows/{hello-world-python,minimal-ml-inference,object-detector-python,opencv-qr-decoder-python,parameter-api-python,pose-estimator-with-flask,web-server}.yml` (triggers L3-9, build steps ≈L29-39); `.github/workflows/example-checks.yml::L17-49`; `.github/workflows/auto-sync-to-staging.yml::L20-53`; `.github/renovate.json`; `.github/ISSUE_TEMPLATE/{bug_report.md, issue-with-custom-model.md}` §Minimum Debug Steps; `.markdownlint.yml`; `.editorconfig`; `.vscode/*`; `.gitignore`; `CODEOWNERS`, at `12.10.0-3-g98b1ea7`.
