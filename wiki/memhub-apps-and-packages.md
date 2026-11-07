---
type: Concept
title: MemHub apps, packages, CLI, i18n and release tooling
description: Workspace layout of MemHub — CLI, Electron desktop, React web UI, site, shared TypeScript packages, runtime-control, i18n, and release/signing scripts.
tags: [memhub, typescript, electron, cli, release, i18n]
status: stable
created: 2026-11-06
generated: { by: llm-wiki-agent/1, at: 2026-11-06T16:45:29Z }
sources:
  - id: hy-memory
    resource: ../raw/Hy-Memory/README.md
    scope: ../raw/Hy-Memory/
    kind: code
    revision: 9737431
    title: Hy-Memory monorepo (hy-memory 2.0.14, MemHub 1.0.6)
---

# MemHub apps, packages, CLI, i18n and release tooling

MemHub is a pnpm workspace (Node ≥ 24, Python 3.12 for Core) of one Python Core plus TypeScript apps and packages (`memhub/package.json` engines; `memhub/pnpm-workspace.yaml` with `disallowWorkspaceCycles: true`; `.python-version`).[^hy-memory]

| Unit | Role | Stack |
|---|---|---|
| `apps/core` | Python FastAPI Core, packaged with PyInstaller (`one-memory.spec`) | see [architecture](memhub-product-architecture.md) |
| `apps/cli` | bins `memhub`, `memhub-cli`, `one-memory` | TS, tsup CJS, vitest |
| `apps/desktop` | Desktop shell | **Electron ^44 + electron-builder** (no Tauri found) |
| `apps/web` | Renderer UI | React 19, Vite 8, TanStack Query, three.js |
| `apps/site` | Static marketing page, never talks to Core | React + Vite |
| `packages/contracts` | Shared wire types, `HOST_ID_PATTERN` | TS sources |
| `packages/host-bridge` | MCP/hook/skill installers, broker client | TS, tsup — see [host bridge](memhub-host-bridge-harness-integration.md) |
| `packages/i18n` | GUI catalogs | i18next |
| `packages/operations` | shared write-operation parser for web + CLI | pure TS |
| `packages/runtime-control` | Runtime install/upgrade/verify, services | TS → `runtime.cjs` |

(`apps/*/package.json`; `packages/*/package.json`; `apps/desktop/package.json` devDependencies; grep for "tauri" returned nothing.)[^hy-memory]

## CLI

36 commands in `apps/cli/src/command-catalog.ts::COMMANDS` (`serve, start, stop, restart, status, doctor, logs, init, sources, sync, progress, jobs, models, memories, profile, settings, evolve, graph-width, host, recall, service-*, install, uninstall, upgrade, delete-data, onboarding, scan, write, backup, ui …`). Exit codes: 0 ok, 1 failed, 2 usage, 3 runtime_stopped, 4 plan_blocked. Only irreversible operations need `--yes`; `delete-data` and `backup restore` also need `--confirm <path>`; host installs are two-phase with `--approve <fingerprint>`; `--user-id` defaults to `local`; `--request-id` gives idempotent retries (`apps/cli/src/exit-codes.ts`; `docs/cli/EXPERIENCE.md`). CLI/App shared-daemon acceptance is marked unverified by the docs, and a stale `~/.one-memory/runtime.json` can make the CLI show `stopped` (Reported).[^hy-memory]

## Desktop and web

The Electron main process serves the web bundle over custom scheme `one-memory://app`, gates every `one-memory:*` IPC handler on trusted windows, and bundles web, PyInstaller core, host-bridge, runtime and cli as `extraResources`; macOS ≥ 13, hardened runtime, dmg arm64+x64, NSIS config for Windows (`apps/desktop/src/main.ts::requireTrustedWindow`, `app-protocol.ts`; `apps/desktop/package.json` `build`). Entitlements include `allow-jit` and `allow-unsigned-executable-memory` (`entitlements/entitlements.mac.plist`).[^hy-memory] The web app has views `memory | sources | health | settings | calls`, an onboarding gate, memory library/raw history/3D graph screens and a dev server pinned to `127.0.0.1:5173` (`apps/web/src/App.tsx`; `vite.config.ts`).[^hy-memory]

## i18n

11 GUI locales plus `system` (`en, zh-Hans, zh-Hant, ja, es, de, pt, fr, ko, ru, id`), legacy `zh-CN → zh-Hans`; catalogs split by feature with English as base, parity enforced by `gui-i18n-locales.test.ts` (`packages/i18n/src/gui-i18n.ts::SUPPORTED_LOCALES`).[^hy-memory]

## runtime-control and release

- Install paths: local distribution dir (`local-install.ts`, manifest with `build_number`, `runtime_protocol`, per-file sha256) and packaged App payload (`packaged-runtime-install.ts`); remote upgrade resolves `release-manifest.json` with a GitHub-host redirect allowlist and proxy support (`release-download.ts`). Verification rejects target mismatch, manifest invalid/incomplete, hash mismatch and wrong Mach-O arch; protocol range is fixed 1..1; downgrades need `--allow-downgrade`; `same_build_replace` keeps the old tree for rollback; services are launchd/systemd user units (`runtime-control/src/*`; `command-catalog.ts::INSTALL_OPTIONS`).[^hy-memory]
- Scripts in `memhub/scripts`: version set/verify, `build-release-assets.mjs`, `build_runtime_distribution.cjs`, macOS build + notarize (`notarytool`, `stapler`; needs Apple API key env vars), Linux verification scripts, `verify-published-release.mjs`, `publish-cli-after-release.mjs`, `generate_sbom.py`, `verify_structure.py`, `verify_zero_collection.py`, `export_public_snapshot.py`.[^hy-memory]
- Release facts: version 1.0.6, build 45, `app_update: "manual"` (`memhub/package.json` `release`).[^hy-memory]

## Gotchas

- No Windows signing/notarization script was found, so Windows release is likely unautomated (Synthesis from absence in `memhub/scripts/platform`).
- CLI tsup inlines `contracts/operations/runtime-control`, so those packages must stay TS-source-only (Synthesis from `apps/cli/tsup.config.ts` comment).
- Web `host-state.ts` carries stale "Pi unsupported" copy per `docs/harness-support/pi.md` (Reported by docs).[^hy-memory]

## Relationships

- Part of: [MemHub architecture](memhub-product-architecture.md).
- Uses: [host bridge](memhub-host-bridge-harness-integration.md).
- CI for these scripts: [releases, CI and quality](hy-memory-release-ci-and-quality.md).

## Coverage and limits

Static inspection (delegated). 283 web files and 94 desktop files were sampled at entry-point level, not read exhaustively; `site` assets, lockfiles and `SBOM.spdx.json` were excluded as generated or decorative.

[^hy-memory]: Hy-Memory monorepo, revision 9737431. Locators inline per claim. Evidence class Observed (delegated static inspection, unexecuted) unless labelled otherwise.
