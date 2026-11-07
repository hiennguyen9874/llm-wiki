---
type: Concept
title: ai-memory distribution, CI, companions and contributor rules
description: How ai-memory is packaged and released (install scripts, brew, AUR, RPM, Scoop, Nix, Docker, macOS app), its CI workflows, companion projects, and contributor gates.
tags: [agent-memory, ai-memory, packaging, ci, contributing, companions]
status: draft
created: 2026-11-06
generated: { by: llm-wiki-agent/1, at: 2026-11-06T16:50:00Z }
stale_after: 2027-02-06
sources:
  - id: readme
    resource: ../raw/ai-memory/README.md
    scope: ../raw/ai-memory/
    kind: code
    revision: 26fa9cf
    title: ai-memory README
  - id: ci
    resource: ../raw/ai-memory/.github/workflows/ci.yml
    scope: ../raw/ai-memory/
    kind: code
    revision: 26fa9cf
    title: CI workflow (and sibling workflows)
  - id: repo-agents
    resource: ../raw/ai-memory/AGENTS.md
    scope: ../raw/ai-memory/
    kind: code
    revision: 26fa9cf
    title: Repository AGENTS.md
  - id: contributing
    resource: ../raw/ai-memory/CONTRIBUTING.md
    scope: ../raw/ai-memory/
    kind: code
    revision: 26fa9cf
    title: CONTRIBUTING.md
  - id: companion-crates
    resource: ../raw/ai-memory/docs/companion-crates.md
    scope: ../raw/ai-memory/
    kind: code
    revision: 26fa9cf
    title: Companion crates
  - id: changelog
    resource: ../raw/ai-memory/CHANGELOG.md
    scope: ../raw/ai-memory/
    kind: code
    revision: 26fa9cf
    title: CHANGELOG.md
  - id: deny
    resource: ../raw/ai-memory/deny.toml
    scope: ../raw/ai-memory/
    kind: code
    revision: 26fa9cf
    title: cargo-deny policy
---

# ai-memory distribution, CI, companions and contributor rules

ai-memory is distributed as a single binary through many channels and developed under strict gates: formatting, clippy with warnings denied, the full nextest suite, `cargo deny`, and a merge-gating CHANGELOG.[^repo-agents][^contributing]

Evidence class: **Observed** (README, workflow/doc heads, `AGENTS.md`; delegated reading for workflow contents); CI results were **not** checked and no build was run. `stale_after` set.

## Distribution channels

- `install.sh` / `install.ps1`: download the release, **refuse to install without a matching published SHA-256**; link `~/.local/bin/ai-memory` (Linux/macOS) or install under `%LOCALAPPDATA%\Programs\ai-memory` (Windows).[^readme]
- Homebrew tap `akitaonrails/tap/ai-memory`; Fedora RPM (`packaging/rpm`); AUR `ai-memory` (source) and `ai-memory-bin`; Scoop bucket (3.4.0+; `upgrade` refuses Scoop installs).[^readme]
- Nix flake with `nixosModules.default` (`services.ai-memory`): dedicated `ai-memory` user and a hardened systemd sandbox; secrets only via agenix/sops/environment file, never in the world-readable store; non-loopback binds require a secret source; `git` is a runtime dependency.[^readme]
- Docker image `akitaonrails/ai-memory` (linux/amd64 and arm64; non-root user; loopback publish in the quick-start).[^readme]
- macOS menu-bar `.app` (Swift, needs Xcode/Swift 6 to build) and an unsigned Tauri desktop installer preview.[^readme][^companion-crates]
- Native `ai-memory upgrade` does checksum-verified GitHub release replacement plus hook refresh.[^readme]

## CI and supply chain

Workflows: `ci.yml` (fmt, clippy, tests, native packaging, pinned Actions, `-D warnings`), `release.yml` (tag-triggered tarballs/zip, GitHub Release, Docker Hub, AUR, Scoop), `codeql.yml`, `secret-scan.yml` (weekly full-history gitleaks), `windows.yml`, `nix.yml`, `desktop.yml`, `macos-app.yml`, `plugins.yml` (real-harness plugin e2e), `sdk-ts-publish.yml` (disabled).[^ci] `deny.toml` ignores one advisory (RUSTSEC-2024-0436, `paste`, compile-time only), allows permissive licenses and denies unknown registries/git sources.[^deny]

## Companions (separate Cargo workspaces; not on crates.io)

`ai-memory-importer` (import documents/OMC wikis/claude_mem/agentmemory vaults as attributed sanitized memory), `ai-memory-relay` (durable SQLite queue → `POST /hook/batch`), `ai-memory-client` (shared capture privacy helpers), `ai-memory-ts` (unpublished TypeScript SDK, zero deps), `ai-memory-wikisync` (one-way export / two-way conditional sync of allowlisted page families into a repo, with a `sync --check` CI gate), `ai-memory-desktop` (Tauri), `ai-memory-macos`.[^companion-crates][^readme]

## Contributor rules

`AGENTS.md` is canonical (`CLAUDE.md` points to it). Gates: `cargo fmt --check`, `git diff --check`, `clippy -D warnings`, `cargo tf` (nextest), `cargo deny check`; a pre-push hook is installable. The CHANGELOG is a merge gate (Unreleased entry under the right heading, past tense, `(#NNN)`, released sections frozen). Core stays Rust-only: anything needing a JS/Swift toolchain lives in `companions/`. Security-boundary tests are "adversarial and mandatory", and destructive ops keep confirmation flags and live-process guards.[^repo-agents][^contributing]

## Release state at the ingested snapshot

Latest released version is **3.4.2 (2026-11-05)** with an `[Unreleased]` section: `run --yolo` becomes the only yolo switch (`--true-yolo` hidden alias); the `api_key` sanitizer no longer matches inside identifiers; `mcp-bridge` adds `resultType: "complete"`; and `restore` no longer restores wiki-git hooks/config (GHSA-w734-2f7h-6qcp).[^changelog]

## Relationships

- Invariants: [Architecture](ai-memory-architecture.md). Security items: [Auth and security](ai-memory-auth-and-security.md). Benchmarks run by CI-adjacent harness: [Evals](ai-memory-evals-and-benchmarks.md).

[^readme]: `../raw/ai-memory/README.md` — "Quick start" subsections (Linux/macOS, Windows, Arch, Homebrew, Fedora, macOS app, Docker, NixOS).
[^ci]: `../raw/ai-memory/.github/workflows/` — file list verified directly; per-workflow purposes read by a delegated agent from workflow heads (`ci.yml` is the declared entry).
[^repo-agents]: `../raw/ai-memory/AGENTS.md` — "Cross-cutting invariants", "Project maintenance rules", "Security considerations".
[^contributing]: `../raw/ai-memory/CONTRIBUTING.md` — gates and CHANGELOG policy.
[^companion-crates]: `../raw/ai-memory/docs/companion-crates.md`; `companions/*/README.md` (each read at head level by a delegated agent).
[^changelog]: `../raw/ai-memory/CHANGELOG.md` — `## [Unreleased]` and the 3.4.2 section (top ~230 lines).
[^deny]: `../raw/ai-memory/deny.toml` — advisories, licenses, sources.
