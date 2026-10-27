---
type: Concept
title: "ACAP Native SDK examples: contribution rules, linters and CI"
description: "The example-structure and coding rules in EXAMPLE_GUIDELINES.md, the super-linter and four custom linters, the build-only per-example CI matrix, disabled Renovate, and the stale or inconsistent items found in the repository tooling."
tags: [edge-ai, axis, acap, examples, ci, lint, maintenance]
status: stable
created: 2026-10-27
generated: { by: llm-wiki-agent/1, at: 2026-10-27T20:00:00Z }
stale_after: 2027-04-30
sources:
  - id: native-examples
    resource: ../raw/acap-native-sdk-examples/README.md
    scope: ../raw/acap-native-sdk-examples/
    kind: code
    revision: "12.11.0-7-g3025a4e (3025a4e9db74f1af5bb878d4efc82ac0e300a792, commit date 2026-09-01)"
    title: "AxisCommunications/acap-native-sdk-examples (git submodule)"
---

# ACAP Native SDK examples: contribution rules, linters and CI

The repository enforces a fixed example shape and a lint suite, and builds every example in CI, but never runs an app or tests on a device.[^native-examples] A change must pass `EXAMPLE_GUIDELINES.md`, the linters in `LINT.md`, and conventional-commit style (`CONTRIBUTING.md`). Codeowners are `@AxisCommunications/acap-native-sdk-owners` and `@AxisCommunications/acap-native-sdk-release-integrators` for all paths (`CODEOWNERS`).

## Example guidelines (`EXAMPLE_GUIDELINES.md`)

- Principles: explain one use case, keep a simple structure, stay short; `axparameter` and `vapix` are named as the canonical examples.
- Required layout `app/{source, LICENSE, Makefile, manifest.json}`, `Dockerfile`, `README.md`; Makefile optional when the architecture is `all`.
- Rules: no `build.sh` scripts, no version numbers in text, a copyright header in every source file, no `http_proxy` baked into a Dockerfile, GCC warnings plus `-Werror` mirroring other examples, C preferred over C++.
- C style: libc first, glib when it shortens code, one-purpose functions, `//` comments explaining why, `main` last, and a fail-fast `panic()` instead of error propagation. This explains why most examples ignore return values.
- README headings: `Title / Project structure / Application description / Build the application / Install and start the application / Expected output / License`.[^native-examples]

## Linters

`run-linters` (`--all`, `--super-linter`, `--renovate-linter`, `--custom-linter`) and VS Code tasks run the same checks as CI.[^native-examples]

| Linter | What it enforces |
| --- | --- |
| super-linter slim, pinned by SHA to v8.7.0 (`.github/workflows/linter.yml`) | `VALIDATE_ALL_CODEBASE=true`; BASH, CLANG_FORMAT, DOCKERFILE_HADOLINT, JSON, MARKDOWN, NATURAL_LANGUAGE, SHELL_SHFMT, YAML (`.github/super-linter.env`) |
| `.clang-format` | LLVM base, 4-space indent, column limit 100, left pointer alignment |
| `.hadolint.yaml` | ignores only DL3008 (apt version pinning) |
| `.textlintrc` | terminology: AXIS OS, VAPIX, ARTPEC-N, ACAP Native SDK, ACAP application, SoC, CPU/GPU/TPU/DLPU, README |
| `lint-acap-documentation-urls.sh` | forbids legacy ACAP doc hosts, doc URLs ending `.md`, absolute self-links to this repo, internal repo links and private Docker Hub URLs |
| `lint-device-urls.sh` | device placeholder must be `AXIS_DEVICE_IP` in allowed forms |
| `lint-example-structure.sh` | every example needs `.github/workflows/<name>.yml` and a matching README list entry |
| `lint-super-linter-version.sh` | `# vN` comment on the pinned action equals every `super-linter:slim-vN` string |
| Renovate validator | `renovate-config-validator` against `.github/renovate.json` |

## CI behaviour

- 31 example workflows plus four `linter*` workflows. Example workflows run on `workflow_dispatch` and on `push` filtered to `<dir>/**` (excluding the README) and the workflow itself; there is **no `pull_request` trigger and no branch filter**, so forked PRs only receive lint checks, never a compile.
- Each job: `ubuntu-latest`, SHA-pinned `actions/checkout` (v7.0.1) and `docker/setup-buildx-action` (v4.2.0 in all but `ptz-control-ws-api.yml`, which uses v3.12.0), `docker build --no-cache --build-arg ARCH=…`, `docker cp` of the package. Permissions are `contents: read`. Nothing is pushed and nothing is executed on a camera.
- Matrices: 25 workflows build `armv7hf` and `aarch64`; chip matrices cover `vdo-larod` (armv7hf cpu/edgetpu; aarch64 artpec8/artpec9/cv25), `object-detection`, `object-detection-yolov5` and `vdostream` (five formats on both arches plus av1/avif/rgb on ARTPEC-9 or CV25); `ptz-control-ws-api` builds armv7hf only; `reproducible-package` runs `reproducible_package.sh` and compares three builds; `tensorflow-to-larod-artpec8` also checks the produced `.tflite` is between 1 MB and 10 GB.
- `tensorflow-to-larod-artpec9.yml` is a placeholder ("dummy workflow", branch `dummy-branch-that-does-not-exist`) that exists to satisfy the structure linter; real testing is delegated to the ARTPEC-8 guide.
- Every example, including every sub-example, has a build; the 41 Dockerfiles are all built somewhere.
- `.github/renovate.json` is `{"enabled": false}`, so SDK, base-image and library versions are bumped by hand.[^native-examples]

## Observed defects and drift

| # | Finding | Evidence |
| --- | --- | --- |
| 1 | Guidelines name MIT as the standard license; root and most `app/LICENSE` files are Apache-2.0 while `device-data-hub`, `ptz-control-ws-api`, `recording-playback` and both axoverlay2 examples are MIT | `EXAMPLE_GUIDELINES.md` licence section vs `LICENSE` files |
| 2 | Only `axparameter`, `licensekey` and `vapix` follow the README heading template; about 40 use "Getting started / How to run the code" | `hello-world/README.md` vs template |
| 3 | `vapix/app/vapix_example.c` lacks the mandatory copyright header; `using-opencv` and `container-example` Makefiles lack `-Werror` | file headers; Makefiles |
| 4 | `LINT.md` is stale (shows `slim-v7`, clang-format 17; claims only changed files are linted although `VALIDATE_ALL_CODEBASE=true`) | `LINT.md`, `super-linter.env` |
| 5 | `.gitignore` uses `//` comments, which git does not honour | `.gitignore` |
| 6 | `run-linters` error text names the non-existent `.github/run-all-linters` | `run-linters` |
| 7 | Every example workflow has an `axis-os: ["12.11.72"]` matrix key that no step reads; the SDK/firmware pairing is not CI-enforced | e.g. `hello-world.yml` |
| 8 | `object-detection-cv25.yml` passes no build args, so its matrix values are decorative | workflow |
| 9 | `tensorflow-to-larod-cv25` builds on unpinned `latest-gpu-py3` | its Dockerfile |
| 10 | `CONTRIBUTING.md` mentions issue templates but `.github/` has none | `CONTRIBUTING.md` |
| 11 | `container-example/postinstall.sh` is committed non-executable while `preuninstall.sh` is executable | file modes |

Items 1–11 are **Observed** from static inspection; no workflow was executed.[^native-examples]

## Relationships

- **Part of** [ACAP Native SDK examples repository](acap-native-sdk-examples-repository.md); build mechanics in [shared conventions](acap-examples-build-and-manifest-conventions.md).
- **Parallels** [CI and maintenance of the ACAP Native SDK repository](acap-native-sdk-repo-ci-and-maintenance.md) (also push-only, SHA-pinned, Renovate disabled) and [CV SDK examples CI](acap-cv-examples-ci-and-maintenance.md).

[^native-examples]: `EXAMPLE_GUIDELINES.md`, `LINT.md`, `CONTRIBUTING.md`, `CODEOWNERS`, `run-linters`, `.github/super-linter.env`, `.github/custom-linters/*.sh`, `.github/renovate.json`, `.github/workflows/*.yml` (`linter*.yml`, `hello-world.yml`, `tensorflow-to-larod-artpec9.yml`, `vdostream.yml`, `ptz-control-ws-api.yml`, `reproducible-package.yml`), `.gitignore`.
