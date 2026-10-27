---
type: Concept
title: "ACAP 3 SDK repository: the Dockerfiles behind the ACAP SDK 3.x image"
description: "What AxisCommunications/acap3-sdk contains at 3.5-aarch64-28-g4e4fe04: two Dockerfiles, a CI check and metadata rather than SDK source, plus identity, license, README claims versus code, release-tag scheme, history and coverage ledger."
tags: [edge-ai, axis, acap, sdk-3, legacy, repository, docker]
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

# ACAP 3 SDK repository: the Dockerfiles behind the ACAP SDK 3.x image

`acap3-sdk` is the packaging repository for the legacy [ACAP SDK version 3](acap-sdk-version-3-legacy.md) developer image, not its source. At the pinned revision the tracked tree is seven files: `README.md`, an Apache-2.0 `LICENSE`, a one-line `CODEOWNERS`, a CI workflow, a Renovate config and two Dockerfiles (`Dockerfile.aarch64`, `Dockerfile.armv7hf`) that assemble the image from two prebuilt Axis images (`acap-api`, `acap-toolchain`).[^acap3-sdk-repo] How the image is assembled is in [image assembly](acap3-sdk-image-assembly.md); how the repo is checked and maintained is in [CI and maintenance](acap3-sdk-repo-ci-and-maintenance.md). It is the ACAP 3 counterpart of the [ACAP Native SDK repository](acap-native-sdk-repository.md), which has the same seven-file shape.

## Identity

| Field | Value |
| --- | --- |
| Upstream | `https://github.com/AxisCommunications/acap3-sdk` (git remote `origin`), checked out at `raw/acap3-sdk/` |
| Revision | `4e4fe046e47dcbbfcdf6bd14b0473e90d8ce5e50` on `main`; `git describe` = `3.5-aarch64-28-g4e4fe04`; commit date 2026-10-01 (merge of PR #52, Renovate `actions/checkout` 7.x) |
| History | 90 commits; first commit 2020-11-24 ("Add initial Dockerfiles for acap-sdk image") |
| License | Apache License 2.0, unmodified text; copyright line "Copyright 2020 Axis Communications AB" in the appendix (`LICENSE`) |
| Owners | `* @AxisCommunications/acap3-sdk-owners`, one catch-all team (`CODEOWNERS` line 1) |
| Languages | Dockerfile, YAML, JSON; no application code |

Evidence class: **Observed** from the files and read-only `git log`, `git describe`, `git tag`, `git ls-tree` and `git diff` runs; nothing was built or executed.[^acap3-sdk-repo]

## What the README says, and where it diverges

The README ("Quick reference") describes an Ubuntu-based image with "all tools for building and packaging an ACAP 3 application" plus the API header and library files for the camera firmware, usable either as a base for custom images or as an in-container developer environment. It points to the ACAP Developer Guide Version 3, the "What's new in ACAP SDK" anchor, the Axis Developer Community, the ACAP product page and the `hello-world` example in `AxisCommunications/acap3-examples` as the worked example of using the image.[^acap3-sdk-repo] These are **Reported** vendor statements; the linked targets are external and not local.

Observed divergences between README and the rest of the repository:

- **Architectures.** The README says "Supported architectures: amd64". The Dockerfiles target `aarch64` and `armv7hf`, and CI builds exactly those two. **Synthesis:** `amd64` is the *host* the image runs on (the Dockerfiles fetch an x86_64 `protoc` and install `crossbuild-essential-*`), so the sentence omits the two *target* architectures. See [image assembly](acap3-sdk-image-assembly.md).
- **License section.** The README says "See the license section at the bottom of this page for restrictions" but contains no such section; the terms are only in `LICENSE`. Commit `d286c77` (2023-09-29, "Remove copyleft notice") removed five README lines, which likely explains the dangling pointer (**Synthesis**; the diff content was not read).
- **Image names.** The README never names a Docker Hub image or tag. The Dockerfiles do not name their own output image either; they name only the `axisecp/acap-api` and `axisecp/acap-toolchain` inputs. The published name `axisecp/acap-sdk:<version>-<arch>-ubuntu<version>` comes from [ACAP SDK version 3 (legacy)](acap-sdk-version-3-legacy.md), from the vendor docs, not from this repo. Nothing in the repo publishes it (see CI page).

## Release-tag scheme and history

Thirty-one tags exist, all of the form `<sdk>-<arch>[-ubuntu<distro>]` (for example `3.1-aarch64`, `3.2-armv7hf-ubuntu19.10`, `3.4.2-aarch64-ubuntu20.04`), plus a bare `3.5`; beta tags are `3.3_beta1-*` and `3.4_beta1-*`. They span SDK 3.1 to 3.5, and HEAD is 28 commits after `3.5-aarch64`.[^acap3-sdk-repo] Selected observations:

- **Tag 3.5 is older than the current Dockerfiles.** `3.5`, `3.5-aarch64` and `3.5-aarch64-ubuntu20.04` all point at `90ac3d9` (2022-02-14, "Update to release 3.5"). At that commit the final stage was `ubuntu:20.04` and the Dockerfile had no KHR step. HEAD differs in three ways: it splits the single `VERSION` arg into `API_VERSION` and `TOOLCHAIN_VERSION`, moves the final base to `ubuntu:22.04` (`7090fe5`, 2022-06-30), and adds the `khrplatform.h` download (`e614d2d`, 2022-06-30). **Synthesis:** HEAD is therefore not what the `3.5-*-ubuntu20.04` tag names describe, and the 22.04 image is untagged here.
- **Tag trees vary.** `3.1-aarch64`/`3.1-armv7hf` point at `2852786` (2022-08-05, a README commit) and their tree includes a `modelconverter.py.patch` that later disappears; the `3.5` tree has the Dockerfiles, README and workflow only. Commit `f26b266` ("Remove Larodconverter which has been replaced") is the matching removal.
- **Dockerfile milestones (Observed from `git log -- Dockerfile.aarch64`).** `3bbf3af` installs `crossbuild-essential-*` from Ubuntu 20.10 to get GCC 10; `2225241` puts the manifest tools on `PATH`; `22ab945`/`a457622` add `protoc` 3.13.0 to match the Axis proto files; `851aa45` adds `--fail` to detect a wrong download; `5c3124e` adds the `python` symlink (mirrored by SDK 3.4.2 in [the legacy page](acap-sdk-version-3-legacy.md)); `9fa1e8b` adds `-Wl,--disable-new-dtags`.
- **Recent history is maintenance only:** Renovate action bumps, SHA pinning and a read-only workflow token (2026-08-18, PRs #53 and #54). The Dockerfiles have not changed since 2022-06-30.

## Coverage ledger

| Artifact | Status |
| --- | --- |
| `README.md` | Inspected in full |
| `Dockerfile.aarch64`, `Dockerfile.armv7hf` | Inspected in full; `diff` shows three differing lines; not built |
| `.github/workflows/build-dockerfile.yml`, `.github/renovate.json`, `CODEOWNERS` | Inspected in full |
| `LICENSE` | Identified as unmodified Apache-2.0; copyright line read; text not compiled |
| Git history and tags | `log` (90 commits), tag list, `diff 3.5 HEAD`, selected `show`; not exhaustively reviewed |
| `.git/` | Used for revision and history only |

## Limits

- The `axisecp/acap-api` and `axisecp/acap-toolchain` images, the `axis-acap-manifest-tools` deb and the published `axisecp/acap-sdk` images are **not local**; claims about their contents come from the Dockerfile text only.
- No Docker build was run, and the 3.5 tag trees were inspected only for file lists and one Dockerfile, so image behavior and registry availability are **Unverified**.
- `stale_after` is set because the base-image tags are mutable and the vendor describes ACAP 3 as superseded by the Native SDK.

## Relationships

- **Packages** the SDK generation documented in [ACAP SDK version 3 (legacy)](acap-sdk-version-3-legacy.md); firmware and chip mapping is in [ACAP generations, chip architectures and compatibility](acap-chip-architecture-and-sdk-compatibility.md).
- **Detailed by** [image assembly](acap3-sdk-image-assembly.md) and [CI and maintenance](acap3-sdk-repo-ci-and-maintenance.md).
- **Superseded by** the [ACAP Native SDK repository](acap-native-sdk-repository.md) for new work (same layout and tooling lineage; see [ACAP Native SDK](axis-acap-native-sdk.md)).
- **Used with** the `hello-world` example of `acap3-examples` (README); the build/install procedure is in [Build, install, and control ACAP applications](acap-build-install-control.md).
- **Source map**: [ACAP documentation repository](acap-documentation-repository.md) holds the vendor SDK 3 docs this repo's README points to.

[^acap3-sdk-repo]: [AxisCommunications/acap3-sdk](../raw/acap3-sdk/README.md) at `4e4fe04`: `README.md` (whole file, headings "Quick reference", "Overview", "ACAP", "How to use the ACAP SDK image"); `LICENSE` header and appendix copyright line; `CODEOWNERS` line 1; `Dockerfile.aarch64` lines 2-11, 15-26, 38-39, 51-58; `git log`, `git tag`, `git describe` output; `git diff 3.5 HEAD`; `git show 7090fe5`; `git ls-tree` at tags `3.1-aarch64` and `3.5`; commit subjects `d286c77`, `f26b266`, `3bbf3af`, `2225241`, `22ab945`, `a457622`, `851aa45`, `5c3124e`, `9fa1e8b`, `e614d2d`.
