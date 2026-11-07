---
type: Concept
title: ai-memory project identity, marker file, auto-scope and cross-project profile
description: How ai-memory decides which project a session belongs to (marker file, auto_scope) and how a small cross-project profile of user habits is injected as defaults.
tags: [agent-memory, ai-memory, scope, profile, configuration]
status: draft
created: 2026-11-06
generated: { by: llm-wiki-agent/1, at: 2026-11-06T16:50:00Z }
sources:
  - id: readme
    resource: ../raw/ai-memory/README.md
    scope: ../raw/ai-memory/
    kind: code
    revision: 26fa9cf
    title: ai-memory README
  - id: marker-file
    resource: ../raw/ai-memory/docs/marker-file.md
    scope: ../raw/ai-memory/
    kind: code
    revision: 26fa9cf
    title: Marker file
  - id: auto-scope
    resource: ../raw/ai-memory/docs/auto-scope.md
    scope: ../raw/ai-memory/
    kind: code
    revision: 26fa9cf
    title: Auto scope
  - id: cross-project-profile
    resource: ../raw/ai-memory/docs/cross-project-profile.md
    scope: ../raw/ai-memory/
    kind: code
    revision: 26fa9cf
    title: Cross-project profile
  - id: usage
    resource: ../raw/ai-memory/docs/usage.md
    scope: ../raw/ai-memory/
    kind: code
    revision: 26fa9cf
    title: Usage guide
---

# ai-memory project identity, marker file, auto-scope and cross-project profile

ai-memory scopes everything to a `(workspace, project)` pair. By default the project name derives from the repository path; a `.ai-memory.toml` marker can override it for multi-client trees, mono-repos, worktrees and work/personal separation, and can route a repository to a different server.[^marker-file] A separate **cross-project profile** carries the user's usual habits into every new repository.[^cross-project-profile]

Evidence class: **Observed** (docs; marker-resolution details were also checked in `hooks/_lib.sh` by a delegated agent); nothing executed.

## Marker file

- Resolution: nearest `.ai-memory.toml`; the walk stops at `$HOME` or the checkout root. Capture-only markers are settings-transparent.[^marker-file]
- Scope precedence: explicit flag → marker / upstream-origin path name → default / cwd basename; supports `identity_style`, aliases, and a `server` profile for per-repository routing.[^marker-file]
- `[capture]` rules in the marker drive capture exclusions and allowlist mode (see [Capture and hooks](ai-memory-capture-and-hooks.md)).[^marker-file]

## `[auto_scope]` (shared servers)

The "current project" pointer is isolated per caller by default since v1.39. Modes: `per_actor` (default, keyed by `(identity, session_id)`), `per_session`, and the pre-v1.39 `single` slot; a read-only startup seed survives restart; an explicit scope fails closed.[^auto-scope][^readme]

## Cross-project profile

A small profile (package manager, test layout, architecture habits) reaches every new repository at session start, sitting *below* each repository's rules file as a default. It is on by default for a single user; on a shared server it is opt-in and private per person. Settings live under `[profile]` (`enabled`, `share`, `min_projects`, budgets); the digest is injected before the handoff and stack-filtered; a team profile needs two operators.[^cross-project-profile][^readme] Documented precedence (each level fills gaps and never overrides the ones above): the user's current instructions → the repository rules file (`CLAUDE.md`/`AGENTS.md`) → project memory (pages, `_rules/`, decisions, gotchas) → cross-project profile; memory "never authorizes anything on its own".[^usage]

## Relationships

- Scope feeds [Handoffs and messaging](ai-memory-handoffs-and-messaging.md) and [authorization](ai-memory-auth-and-security.md) (per-project grants).
- Profile synthesis is an LLM workload in [Consolidation and aging](ai-memory-consolidation-and-aging.md) / [providers](ai-memory-llm-and-embedding-providers.md).

[^readme]: `../raw/ai-memory/README.md` — "It follows you across projects"; "Quick start" (auto-scope paragraph).
[^marker-file]: `../raw/ai-memory/docs/marker-file.md` — "Who reads the marker", "Capture exclusions".
[^auto-scope]: `../raw/ai-memory/docs/auto-scope.md` — modes and fail-closed notes.
[^cross-project-profile]: `../raw/ai-memory/docs/cross-project-profile.md` — "Server settings"; defaults, opt-outs, multi-user privacy.
[^usage]: `../raw/ai-memory/docs/usage.md` — "Rules, memory and the profile" (ordered precedence list, lines ~957–980).
