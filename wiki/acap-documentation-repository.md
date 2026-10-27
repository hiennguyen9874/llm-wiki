---
type: SourceMap
title: "ACAP documentation repository (archived Jekyll site)"
description: "What the archived AxisCommunications/acap-documentation repository contains, how it was built, linted and redirected, a coverage ledger of its 3,182 files mapped to wiki concepts, and the stale or defective items found in it."
tags: [edge-ai, axis, acap, documentation, source-map, jekyll]
status: stable
created: 2026-10-27
generated: { by: llm-wiki-agent/1, at: 2026-10-27T22:00:00Z }
stale_after: 2027-04-30
sources:
  - id: acap-docs-repo
    resource: ../raw/acap-documentation/README.md
    scope: ../raw/acap-documentation/
    kind: code
    revision: "12.2-17-g4aa04f1 (4aa04f185618e66f493453bcd62da1788c3059e4, 2025-02-06)"
    title: "ACAP documentation (archived repository)"
  - id: acap-docs-contributing
    resource: ../raw/acap-documentation/CONTRIBUTING.md
    scope: ../raw/acap-documentation/CONTRIBUTING.md
    kind: docs
    revision: "12.2-17-g4aa04f1"
    title: "Contributing to the ACAP documentation"
  - id: acap-docs-lint-ci
    resource: ../raw/acap-documentation/.github/workflows/lint.yml
    scope: ../raw/acap-documentation/.github/
    kind: code
    revision: "12.2-17-g4aa04f1"
    title: "Lint workflow, super-linter environment and device-URL check"
---

# ACAP documentation repository (archived Jekyll site)

`AxisCommunications/acap-documentation` is the pre-2025 source of the public ACAP documentation, a Jekyll site using the *Just the Docs* theme. It is frozen: its README says the repository "has been archived and its content migrated to Axis Developer Documentation" at `developer.axis.com/acap`, and every one of its 101 documentation pages (plus `index.md` and `404.html`) carries a `redirect_to` front-matter key pointing at the live site.[^acap-docs-repo] The local snapshot is therefore the **frozen pre-migration text**: it is the only place in `raw/` that holds pages the newer `raw/acap/` capture lacks — the ACAP version history, the release notes 4.0 to 12.2, the Axis devices and compatibility tables, the manifest-schema 1.x field pages, the Native SDK API list, the FAQ, and the whole ACAP SDK version 3 documentation. This page is the coverage ledger for that package and records where each part went.

## Identity

| Item | Value |
| --- | --- |
| Upstream | `AxisCommunications/acap-documentation` on GitHub (archived) |
| Snapshot | git describe `12.2-17-g4aa04f1`; merge of PR #164 `sync-20250206-1`, committed 2025-02-06; tags `12.0`, `12.1`, `12.2` |
| Languages and tooling | Markdown (kramdown), Ruby/Jekyll, Python helper scripts, Bash |
| Licence | `LICENSE` is "Copyright (C) 2021 Axis Communications AB. All rights reserved." with a trademark notice, not an open-source licence; the theme is MIT (`docs/licenses/index.md`); example code under the API trees carries its own `LICENSE` files |
| Audience | ACAP application developers for the Native SDK, the retired Computer Vision SDK and ACAP SDK 3 |

Because every page redirects, the live page is authoritative where it differs; the archived body is the evidence used here.[^acap-docs-repo] Evidence class for statements below is **Observed** (static inspection of the snapshot) unless marked otherwise; nothing was built or executed.

## Coverage ledger

| Area | Files | Status | Destination |
| --- | ---: | --- | --- |
| `docs/introduction/`, `index.md` | 7 | Inspected | [ACAP generations and compatibility](acap-chip-architecture-and-sdk-compatibility.md), [ACAP developer FAQ and help channels](acap-developer-faq.md) |
| `docs/get-started/**` | 6 | Inspected; reconciled | Already covered by [Preparing an Axis device](axis-device-setup.md), [SSH and Developer Mode](axis-device-ssh-developer-mode.md) and [Developer environment](acap-dev-environment-setup.md); the Docker Engine ≥ 23.0.0 prerequisite is recorded in the compatibility page |
| `docs/faq/**`, `docs/cloud-integrations/`, `docs/get-help-and-give-feedback/`, `docs/licenses/` | 7 | Inspected | [Fleet deployment with upload.cgi and control.cgi](acap-fleet-deployment-via-vapix.md), [ACAP developer FAQ](acap-developer-faq.md) |
| `docs/axis-devices-and-compatibility/` | 1 | Inspected | [ACAP generations and compatibility](acap-chip-architecture-and-sdk-compatibility.md); the container half matches [Container application compatibility](acap-container-compatibility.md) |
| `docs/develop/*.md` (11 pages) | 11 | Inspected; reconciled | Already covered by existing build, user, VAPIX, proxy, web-server, third-party-library, calibration and manifest-migration concepts; contradictions below |
| `docs/develop/manifest-schemas/` | 13 | Inspected | [Manifest schema 1.x history](acap-manifest-schema-v1-history.md) |
| `docs/develop-container-applications/` | 6 | Inspected; deprecation stubs | [Container-based ACAP applications](acap-container-applications.md) |
| `docs/release-notes/` | 21 | Inspected | [ACAP release history 4.0 to 12.2](acap-release-history.md) |
| `docs/service/` | 3 | Inspected | Already covered by [ACAP application signing](acap-application-signing.md); the enforcement table matches |
| `docs/api/*.md`, `_setup_apidocs.sh` | 5 | Inspected | [Native SDK API catalog](acap-native-sdk-api-catalog.md) |
| `docs/acap-sdk-version-3/*.md` (non-generated) | 22 | Inspected | [ACAP SDK version 3 (legacy)](acap-sdk-version-3-legacy.md) |
| `docs/api/src/` | 890 | Inventoried, not read page by page | Generated Doxygen HTML; library list in the API catalog |
| `docs/acap-sdk-version-3/api/src/` | 1,052 | Inventoried | Generated Doxygen HTML for ACAP 3 |
| `3.5/` | 1,052 | Excluded: duplicate | Byte-identical to the previous tree except three redirect stubs |
| `3.4/` | 49 | Excluded: unreferenced | Only the deprecated `capture` API plus stubs |
| `Dockerfile`, `Dockerfiles-multistage/`, `build-multistage`, `build_redirects.py`, `_config.yml`, `Gemfile`, `.github/`, linter configs, `_layouts/`, `_includes/`, `_sass/` | ~25 | Inspected | This page |
| `assets/`, `favicon.ico`, `.vscode/` | 7 | Listed; images not viewed (decorative VS Code screenshots and logos) | Excluded |

The generated trees total about 3,043 files (HTML, JS, PNG, CSS, Doxygen `.dot` and `.md5` caches, and original C example sources); they are cited only as an inventory, not as claim evidence, apart from version markers in page headers (see the API catalog).[^acap-docs-repo]

## Build, preview and CI

- **Preview**: `docker build -t doc:1 .` from the repo root, then `docker run … -v "$ACAPDOC":/srv/jekyll -it doc:1 jekyll serve` guarded so the directory name must be `acap-documentation*`; served at `http://0.0.0.0:4000/acap-documentation`. The guard exists so the Jekyll image cannot change ownership of unrelated user directories.[^acap-docs-contributing]
- **Image**: `Dockerfile` uses `jekyll/jekyll:3.8`, deletes any `Gemfile.lock`, and pins `bundler -v 2.4.22`; `Gemfile` requests `github-pages ~> 231` and `just-the-docs ~> 0.10.0`, while `_config.yml` uses an unpinned `remote_theme: just-the-docs/just-the-docs`. `build-multistage [full|conf]` builds two staged images so a config-only rebuild takes about ten seconds.[^acap-docs-repo]
- **Lint**: `.github/super-linter.env` enables Markdown (`.markdownlint.yml`, which disables MD013, MD025, MD028, and relaxes MD024/MD033) and natural-language checks (`.textlintrc` terminology rules such as `ARTPEC-N`, `AXIS OS`, `SoC`, `README`). Generated trees are excluded by regex. `lint.yml` also fails on private Docker Hub URLs (`hub.docker.com/repository/docker/axisecp`) and runs `lint-device-urls.sh`, which allows only the device address `192.168.0.90` in examples.[^acap-docs-lint-ci]
- **Workflows**: `lint.yml` (push, pull request, manual; super-linter slim v7), `build-dockerfiles.yml` (push only; builds the image and runs `./build-multistage full`), `manifest-schemas.yml` (fails if the schema index still contains the placeholder `ADD-MANIFEST-SCHEMA-RELEASE-DESCRIPTION`).[^acap-docs-lint-ci]
- **Contribution rules**: generated files must not be edited here (`docs/api/**` and the manifest `schema-field-descriptions-*.md` pages); conventional commits; 80-column prose; Beta APIs are marked `BETA -` and link `beta-api`; `CODEOWNERS` assigns `*` to `@AxisCommunications/acap-documentation-owners`.[^acap-docs-contributing]
- **Redirect migration**: `build_redirects.py` is a one-shot script that injected `redirect_to: https://developer.axis.com/acap/<path>` into every page, with hand-written remaps for section indexes (for example `get-started/` → `…/pre-requisites`, `service/` → `…/acap-service-portal`).[^acap-docs-repo]

## Stale or defective items found

All are **Observed** by static inspection:

- `index.md` links `./docs/version-history`, which does not exist; the page is `docs/introduction/version-history.md`.
- `version-history.md` lists only ACAP 12 (2024), while the compatibility page and release notes document 12.0, 12.1 and 12.2; it also still calls ACAP 3 and 4 "Actively maintained".
- `docs/introduction/acap-sdk-overview.md` shows "App Deployment: Docker" for the deprecated Computer Vision solution, whereas its own body routes AXIS OS 12.0+ through Docker ACAP, Docker Compose ACAP and ACAP Runtime.
- `docs/get-started/hello-world-example.md` still routes the container path to the archived Computer Vision SDK examples.
- `docs/develop/application-project-structure.md` lists a Preupgrade Script (AXIS OS 9.30) as an optional file but, in the same page, says pre-upgrade scripts are not supported with `manifest.json`; its dynamic-user paragraph omits the `.setup.` segment of `acapPackageConf.setup.user.*`.
- `docs/develop/build-install-run.md` describes `-t` in `docker run` as the repository tag; it is the tty flag.
- `docs/develop/camera-calibration.md` places the code under `acap-sdk-tools` in one place and `acap-sdk-extras` in another. The `acap-sdk-tools` repository is now local; see [ACAP SDK tools repository](acap-sdk-tools-repository.md).
- `docs/faq/deployment.md` uses different multipart field names for the same endpoint (see [Fleet deployment](acap-fleet-deployment-via-vapix.md)).
- Manifest-schema constraints added in 1.4.0 to 1.7.3 appear only in `manifest-schemas/index.md`, not in the per-version field pages.
- Repository hygiene: no `.dockerignore` (the image copies `.git` and the 11 MB Doxygen copies), unreferenced `favicon.ico`, a no-op `manifest-schemas.yml` guard, `3.4/` and `3.5/` not excluded from Jekyll.

## Limits

- The generated Doxygen trees were inventoried and sampled, not read exhaustively; API behaviour is taken from the prose list pages, not from header documentation.
- External targets (GitHub repositories, `help.axis.com`, the Product selector, VAPIX library, CFC Portal) are not local and were not checked.
- Redirect targets on `developer.axis.com` were not fetched; the local `raw/acap/` capture is a different, later snapshot and is reconciled by the existing concepts, not by this page.

## Relationships

- **Superseded by** the live Axis Developer Documentation, which the local `raw/acap/` capture mirrors at a later date.
- **Feeds** [ACAP release history 4.0 to 12.2](acap-release-history.md), [Manifest schema 1.x history](acap-manifest-schema-v1-history.md), [Native SDK API catalog](acap-native-sdk-api-catalog.md), [ACAP SDK version 3 (legacy)](acap-sdk-version-3-legacy.md), [ACAP generations and compatibility](acap-chip-architecture-and-sdk-compatibility.md), [Fleet deployment](acap-fleet-deployment-via-vapix.md) and [ACAP developer FAQ](acap-developer-faq.md).
- **Complements** [ACAP Native SDK](axis-acap-native-sdk.md) and [ACAP version rules](acap-versioning.md): those pages were compiled from the later `raw/acap/` capture and noted that the version-history and compatibility pages were missing; this snapshot supplies them.

[^acap-docs-repo]: [README](../raw/acap-documentation/README.md) archive notice; `_config.yml` (`remote_theme`, `baseurl`, plugins); `Dockerfile`; `build_redirects.py`; `docs/licenses/index.md`; `LICENSE`; front matter `redirect_to` on all pages under `docs/`. Revision `12.2-17-g4aa04f1`. File counts from `find` over the snapshot.
[^acap-docs-contributing]: [CONTRIBUTING.md](../raw/acap-documentation/CONTRIBUTING.md), preview commands, rules for generated files, commit style and writing conventions; `TROUBLESHOOTING.md` §Avoid accidental ownership change; `CODEOWNERS`.
[^acap-docs-lint-ci]: [lint.yml](../raw/acap-documentation/.github/workflows/lint.yml) and sibling `build-dockerfiles.yml`, `manifest-schemas.yml`; `.github/super-linter.env`; `.github/lint-device-urls.sh`; `.markdownlint.yml`; `.textlintrc`.
