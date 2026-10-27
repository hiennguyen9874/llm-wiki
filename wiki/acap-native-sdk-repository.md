---
type: Concept
title: "ACAP Native SDK repository: the Dockerfiles behind the SDK image"
description: "What AxisCommunications/acap-native-sdk actually contains at 12.10.0-2: two Dockerfiles, a CI check and metadata rather than SDK source code, plus identity, license, revision and coverage ledger."
tags: [edge-ai, axis, acap, sdk, repository, docker]
status: stable
created: 2026-10-27
generated: { by: llm-wiki-agent/1, at: 2026-10-27T19:00:00Z }
stale_after: 2027-04-30
sources:
  - id: acap-native-sdk-repo
    resource: ../raw/acap-native-sdk/README.md
    scope: ../raw/acap-native-sdk/
    kind: code
    revision: "12.10.0-2-geed6dcf (eed6dcff23c17e744b773473646251752b91184f, 2026-08-18)"
    title: "AxisCommunications/acap-native-sdk (git submodule)"
---

# ACAP Native SDK repository: the Dockerfiles behind the SDK image

The `acap-native-sdk` repository is not where the SDK's code lives. At the pinned revision its whole tracked tree is seven files: a short README, an Apache-2.0 `LICENSE`, a one-line `CODEOWNERS`, a CI workflow, a disabled Renovate config and two Dockerfiles (`Dockerfile.aarch64`, `Dockerfile.armv7hf`) that assemble the SDK developer image from two prebuilt Axis images.[^acap-native-sdk-repo] Everything a developer gets from the SDK (headers, libraries, cross toolchain, manifest tools) comes from images this repo only *composes*; how it composes them is in [SDK image assembly](acap-native-sdk-image-assembly.md), what it removes in [sysroot pruning](acap-native-sdk-sysroot-pruning.md), and how it is checked and maintained in [CI and maintenance](acap-native-sdk-repo-ci-and-maintenance.md).

## Identity

| Field | Value |
| --- | --- |
| Upstream | `https://github.com/AxisCommunications/acap-native-sdk` (git remote `origin`), vendored here as a submodule at `raw/acap-native-sdk/` |
| Revision | `eed6dcff23c17e744b773473646251752b91184f` on `main`, `git describe` = `12.10.0-2-geed6dcf`, commit date 2026-08-18 |
| Release tags | `12.10.0` and `12.11.0` both point at `030dc43` (2026-05-04), one commit before the two 2026-08-18 commits; HEAD itself is untagged. 105 tags exist in total. `12.11.0` also lives on `origin/rel/fw-12.11/maint` |
| License | Apache License 2.0, unmodified text (`LICENSE`) |
| Owners | `* @AxisCommunications/acap-native-sdk-owners`, a single catch-all team (`CODEOWNERS` line 1) |
| Languages | Dockerfile, YAML, JSON; no application code |
| First commit | 2021-03-17; 97 commits in history |

Evidence class: **Observed** from the files and from read-only `git log`, `git describe`, `git tag` and `git ls-tree` runs; nothing was built or executed.[^acap-native-sdk-repo]

## What the README says

The README (`README.md`) is a platform blurb, not technical documentation. It defines ACAP as an open application platform for Axis cameras, speakers and intercoms, positions the Native SDK for "plug-in style, event generating applications that fit well into a VMS centric system" with "high performance by integrating closely with AXIS OS and hardware", and links to the [ACAP documentation](https://axiscommunications.github.io/acap-documentation/) and to the `acap-native-sdk-examples` repository (see [official application examples](acap-application-examples.md)). **Reported:** these are vendor positioning statements with no benchmarks.[^acap-native-sdk-repo]

## The repository has been Dockerfile-only for a long time

**Observed:** `git ls-tree -r` lists the same seven files at tags `1.15.3`, `12.0.0`, `12.9.0` and HEAD, so the repository has held only Dockerfiles and metadata across the ACAP 1.x to 12.x range inspected; the SDK payload is not versioned here.[^acap-native-sdk-repo] The README's "ACAP Native SDK" is therefore a packaging repository for the image published by Axis as `axisecp/acap-native-sdk` (**Synthesis**: the Dockerfiles name only the `axisecp` base repositories `acap-api` and `acap-toolchain` and never state their own output image name; the `axisecp/acap-native-sdk:<version>-<arch>-<ubuntu>` tag form comes from the compatibility and setup concepts below).

## Recent history that explains the current files

Subjects below are **Observed** from `git log`; for the first, fourth and fifth rows the diffs were also read.[^acap-native-sdk-repo]

| Commit | Date | Change |
| --- | --- | --- |
| `eed6dcf` (#89) | 2026-08-18 | Pin GitHub Actions to commit SHAs |
| `6ee96ae` (#88) | 2026-08-18 | Default workflow token permissions set to read-only |
| `030dc43` (#87) | 2026-05-04 | Add `nlohmann_json.pc` copy step to both Dockerfiles |
| `19ec803` (#86) | 2026-05-04 | Remove `libpaho` from the SDK (one line per Dockerfile) |
| `44ef0ff` (#85) | 2026-03-12 | "compatibleOSVersion in SDK": add `AXIS_OS_VERSION_TAG` build arg and `AXIS_OS_VERSION` env |
| `0423873` (#84) | 2026-02-10 | Disable the Renovate bot |
| `b351c0b` | 2025-11-05 | Revert of PR #5 (`changes/remove-api/libnlohmann`); it deletes the `libnlohmann*` and `nlohmann` block-list entries that `8b054d1` (2025-11-04) had added |
| `0751145` (#74) | 2025-06-13 | Re-add `axaudio` and `axhttp` APIs by deleting them from the removal lists |
| `0d8c0cb` (#73) | 2025-04-24 | armv7hf: replace `-D_TIME_BITS=32` / `-D_FILE_OFFSET_BITS=32` with `-U_TIME_BITS` / `-U_FILE_OFFSET_BITS` |

The pattern worth retaining (**Synthesis**): changes to the SDK's public surface are made as edits to *removal lists* in the Dockerfiles, so the repo history is the audit trail for which Axis OS libraries are visible to ACAP applications.

## Coverage ledger

| Artifact | Status |
| --- | --- |
| `README.md` | Inspected |
| `Dockerfile.aarch64`, `Dockerfile.armv7hf` | Inspected statically in full; compared with `diff`; not built |
| `.github/workflows/build-dockerfile.yml`, `.github/renovate.json`, `CODEOWNERS` | Inspected |
| `LICENSE` | Identified as Apache-2.0; text not compiled |
| `.git` (submodule pointer file) | Inspected for revision only |
| Git history | Read through `log`, `describe`, `tag`, `ls-tree` and selected `show` output; not exhaustively reviewed |

## Limits

- The base images `axisecp/acap-api` and `axisecp/acap-toolchain`, the `axis-acap-manifest-tools` deb, the `environment-setup*` script and the resulting sysroot are **not local**; claims about what they contain are inferred from the Dockerfile text only.
- No Docker build was run, so the effective contents of the image and the network behavior of the build are **Unverified**.
- `stale_after` is set because the base image tags default to `latest` and the removal lists change between releases.

## Relationships

- **Packages** the image used by [Build, install, and control ACAP applications](acap-build-install-control.md) and [ACAP development environment setup](acap-dev-environment-setup.md) (`axisecp/acap-native-sdk:<version>-<arch>-ubuntu<version>`).
- **Detailed by** [SDK image assembly](acap-native-sdk-image-assembly.md), [sysroot pruning](acap-native-sdk-sysroot-pruning.md) and [CI and maintenance](acap-native-sdk-repo-ci-and-maintenance.md).
- **Implements** the Docker-based toolchain described in [ACAP Native SDK and the Axis camera platform](axis-acap-native-sdk.md); architecture names and SDK-to-AXIS OS mapping are in [ACAP generations, chip architectures and compatibility](acap-chip-architecture-and-sdk-compatibility.md).
- **Succeeds** the [ACAP 3 SDK repository](acap3-sdk-repository.md), the same seven-file Dockerfile-composition layout for the legacy ACAP SDK 3.x ([legacy SDK](acap-sdk-version-3-legacy.md)); unlike it, this repo prunes the sysroot and has Renovate disabled.
- **Complements** [Official ACAP application examples](acap-application-examples.md): the examples repository is the code, this one the build environment.

[^acap-native-sdk-repo]: [AxisCommunications/acap-native-sdk](../raw/acap-native-sdk/README.md) at `eed6dcf`: `README.md` (whole file); `LICENSE` header; `CODEOWNERS` line 1; `git ls-tree -r` at tags `1.15.3`, `12.0.0`, `12.9.0` and HEAD; `git log`, `git tag`, `git describe` output; commit diffs of `44ef0ff`, `0751145`, `0d8c0cb`, `0423873`.
