---
type: Concept
title: ai-memory overview
description: Entry point to ai-memory, a Rust single-binary long-term memory server for AI coding agents that stores memory as a git-backed markdown wiki and works with zero LLM calls by default.
tags: [ai-memory, agent-memory, rust, overview]
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
  - id: cargo
    resource: ../raw/ai-memory/Cargo.toml
    scope: ../raw/ai-memory/
    kind: code
    revision: 26fa9cf
    title: ai-memory workspace Cargo.toml
---

# ai-memory overview

**ai-memory** is long-term memory for AI coding agents: quit one agent mid-task (e.g. Claude Code), start another (e.g. Codex) in the same directory, and continue without re-explaining the architecture, failed approaches, or open questions.[^readme] It ships as one self-contained Rust binary that runs an MCP/HTTP server over a single data directory.[^readme] The source of truth is a git-backed wiki of ordinary markdown files; the SQLite database is a derived index that can be rebuilt from those files.[^readme] The default path makes **zero LLM calls** (capture, search and handoffs work without any API key); The README describes LLM consolidation, vector search and the "dream" rewrite as opt-in.[^readme] The effective default embedding configuration warrants particular care: the [providers page](ai-memory-llm-and-embedding-providers.md) records a local embedder default when the provider is unset.

Evidence class: **Observed** (static inspection of the README and `Cargo.toml` at the pinned revision; the README's marketing-style claims are **Reported**, not independently verified). Nothing was built or executed.

## Identity

| Item | Value |
| --- | --- |
| Upstream | `github.com/akitaonrails/ai-memory`, site `aimemory.sh`[^cargo] |
| Workspace version | 3.4.2, edition 2024, `rust-version` 1.95, license MIT[^cargo] |
| Snapshot ingested | commit `26fa9cf` = `v3.4.2-56-g26fa9cf46`, i.e. 56 commits past the 3.4.2 tag (git describe, observed locally) |
| Default bind | `127.0.0.1:49374` (loopback)[^readme] |

## The pitch in five axes

The README claims memory that follows you across **agents** (20+ harnesses feeding one memory), **projects** (a small cross-project profile), **machines** (server you run anywhere) and **teams** (per-project sharing, multi-user auth, audit log), while staying **plain markdown** you can `grep`, open in Obsidian or `rsync`.[^readme] (Reported.)

## Pipeline: capture → consolidate → recall → handoff

1. Lifecycle hooks silently record sanitized observations (prompts, tool calls, session boundaries) — see [Capture and hooks](ai-memory-capture-and-hooks.md).[^readme]
2. At session end, observations become markdown pages (a deterministic page by default, optionally LLM-written) — see [Consolidation and aging](ai-memory-consolidation-and-aging.md).[^readme]
3. The next session, in any agent, gets a bounded brief and can search with FTS, entities, links and optional vectors fused into one ranking — see [Retrieval pipeline](ai-memory-retrieval-pipeline.md).[^readme]
4. Cross-agent handoffs pass the baton explicitly, claim-once — see [Handoffs and messaging](ai-memory-handoffs-and-messaging.md).[^readme]

## Map of the ai-memory pages

- Design and storage: [Architecture and crates](ai-memory-architecture.md), [Wiki storage, OKF, typed edges, temporal](ai-memory-wiki-storage-and-okf.md).
- Capture and agents: [Capture and hooks](ai-memory-capture-and-hooks.md), [Harness integrations and CLI](ai-memory-harness-integrations-and-cli.md), [Managed workstreams](ai-memory-managed-workstreams.md), [Handoffs and messaging](ai-memory-handoffs-and-messaging.md), [Project identity and cross-project profile](ai-memory-project-identity-and-profile.md).
- Recall and surfaces: [Retrieval pipeline](ai-memory-retrieval-pipeline.md), [MCP tools and HTTP surfaces](ai-memory-mcp-tools-and-http-surfaces.md).
- Trust and operations: [Auth and security](ai-memory-auth-and-security.md), [Data handling and lifecycle ops](ai-memory-data-handling-and-lifecycle-ops.md), [Distribution, CI and companions](ai-memory-distribution-ci-and-companions.md).
- Intelligence: [Consolidation and aging](ai-memory-consolidation-and-aging.md), [Auto-improvement and rules promotion](ai-memory-auto-improvement.md), [LLM and embedding providers](ai-memory-llm-and-embedding-providers.md), [Evals and benchmarks](ai-memory-evals-and-benchmarks.md).
- Context and limits: [Comparison claims](ai-memory-comparison-claims.md), [Source map and documentation discrepancies](ai-memory-source-map-and-doc-discrepancies.md).

## Lineage

The README names its influences: the Karpathy LLM Wiki (compile-not-retrieve), agentmemory (hook capture), basic-memory (markdown-on-disk truth), cognee (pipeline composition, triplet embeddings), Hermes Agent (self-improvement loop) and A-MEM (Zettelkasten-style atomic notes).[^readme] It also states the codebase is built collaboratively with Claude Code.[^readme]

## Relationships

- Uses: [Wiki storage and OKF](ai-memory-wiki-storage-and-okf.md) as its on-disk format (OKF v0.2 bundle).
- Related repositories in this knowledge base's `raw/` folder (mem0, cognee, hindsight, memos, gbrain, etc.) are separate sources; this page makes no claim about them beyond the README's self-reported comparison ([Comparison claims](ai-memory-comparison-claims.md)).

[^readme]: `../raw/ai-memory/README.md` — "Why ai-memory" (axes, zero-LLM default, plain markdown), "How it works" (pipeline), "Support matrix", "Quick start" (default bind `127.0.0.1:49374`), "Architecture" (data dir layout), "Built on the shoulders of", "Acknowledgements".
[^cargo]: `../raw/ai-memory/Cargo.toml::[workspace.package]` — `version = "3.4.2"`, `edition = "2024"`, `rust-version = "1.95"`, `license = "MIT"`, repository and homepage fields.
