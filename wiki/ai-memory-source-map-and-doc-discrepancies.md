---
type: SourceMap
title: ai-memory source map, coverage ledger and documentation discrepancies
description: Coverage ledger for the ai-memory snapshot ingested on 2026-11-06 (what was inspected, excluded or pending) and the doc-versus-code discrepancies found.
tags: [agent-memory, ai-memory, source-map, coverage, discrepancies]
status: draft
created: 2026-11-06
generated: { by: llm-wiki-agent/1, at: 2026-11-06T16:50:00Z }
sources:
  - id: readme
    resource: ../raw/ai-memory/README.md
    scope: ../raw/ai-memory/
    kind: code
    revision: 26fa9cf
    title: ai-memory README (entry point of the package)
---

# ai-memory source map, coverage ledger and documentation discrepancies

This page is the idempotency ledger for the package `raw/ai-memory/` (a git submodule of `github.com/akitaonrails/ai-memory`) at commit `26fa9cf` (`v3.4.2-56-g26fa9cf46`, observed by `git describe`/`git log` in the submodule). The entry point is the README.[^readme] Status is `draft` because coverage is partial and mostly delegated.

## Method and limits

Exploration used five parallel read-only Explore subagents with disjoint slices (core/storage; capture/harnesses; retrieval/MCP/web; consolidation/LLM/evals; security/ops/packaging). The curator read the README fully and spot-checked directly: workspace version, edition and required Rust version, and migration file count (101 files; V101 head was reported by a delegate, not independently confirmed), MCP tool attribute count (27), the decay defaults (`λ=0.02, σ=0.6, μ=0.04`), default bind constants, the LongMemEval-S 3.4.0 report, `AGENTS.md` invariants (≥16), the CHANGELOG `[Unreleased]` head, and `docs/usage.md` precedence. Everything else is **delegated static reading** — not re-verified by me. No project code was built, run or tested; no CI results were consulted. Sensitive-value screen: the README's Docker example uses placeholder keys; delegated agents were instructed not to disclose secrets. A complete repository-wide secret or disclosure-boundary scan was not performed; inspected inputs are limited to the listed files.[^readme]

## Coverage ledger

| Area | Status | Concept page |
| --- | --- | --- |
| README, Cargo.toml, rust-toolchain | inspected | [overview](ai-memory-overview.md), [architecture](ai-memory-architecture.md) |
| `docs/ARCHITECTURE.md`, `okf.md`, `typed-edges.md`, `temporal.md`, `wiki-migrations.md`, `design-decisions.md` §3–7 | inspected (delegated) | [architecture](ai-memory-architecture.md), [wiki storage](ai-memory-wiki-storage-and-okf.md) |
| crates `core`, `store`, `wiki` | inspected selectively (lib roots, schema, key modules) | same |
| `hooks/`, `plugins/`, crates `hooks`, `workstream`, CLI `cli.rs`/`hook.rs` | inspected selectively | [capture](ai-memory-capture-and-hooks.md), [harnesses](ai-memory-harness-integrations-and-cli.md), [workstreams](ai-memory-managed-workstreams.md), [handoffs](ai-memory-handoffs-and-messaging.md), [identity](ai-memory-project-identity-and-profile.md) |
| crates `mcp`, `web`; user/API docs | inspected selectively | [retrieval](ai-memory-retrieval-pipeline.md), [MCP/HTTP](ai-memory-mcp-tools-and-http-surfaces.md) |
| crates `consolidate`, `llm`; aging/auto-improve/provider docs | inspected | [consolidation](ai-memory-consolidation-and-aging.md), [auto-improve](ai-memory-auto-improvement.md), [providers](ai-memory-llm-and-embedding-providers.md) |
| `evals/`, `docs/benchmarks/` | 3.4.0 report read directly; others delegated; older releases (3.0–3.3) skimmed only | [evals](ai-memory-evals-and-benchmarks.md) |
| `SECURITY.md`, `DATA_HANDLING.md`, ops docs, packaging, `.github`, `companions/` | inspected at head level | [security](ai-memory-auth-and-security.md), [data handling](ai-memory-data-handling-and-lifecycle-ops.md), [distribution](ai-memory-distribution-ci-and-companions.md) |
| `docs/comparison.md`, `research-*`, `issues-*` | banners and key sections only | [comparison](ai-memory-comparison-claims.md) |
| `CHANGELOG.md` | top ~230 lines | [distribution](ai-memory-distribution-ci-and-companions.md) |
| `Cargo.lock`, `flake.lock`, images (`logo-*.png`, `architecture-overview.svg`, `web-project-view.png`), `tests/`, most of `docs/design-*`, `docs/examples/`, `docs/changelog/*`, `.git/`, per-harness hook bodies beyond Claude Code/Codex | **pending / excluded** (lock files and images decorative or generated; the architecture SVG and screenshot were **not** inspected visually) | — |
| `docs/sso.md`, `docs/deploy.md`, `docs/backup.md`, `docs/windows.md`, `docs/macos.md`, `docs/use-cases.md`, `docs/cookbook.md`, `docs/install.md` | skimmed or grepped only | referenced where relevant |

Idempotency rule for a future run: reconcile against this ledger; only pending rows and changed revisions should trigger new work.

## Documentation vs implementation discrepancies

All **Observed by delegated inspection** unless stated; none re-verified except where noted.

1. `docs/design-file-path-index.md` ("highest migration is V97") and `docs/design-message-decisions.md` ("V80") are stale; head is **V101** (head verified by me).
2. `V62__page_ingestion_windows.sql` header mentions `set_abort_divergent(false)`; `migrations.rs::run` uses `true` and repairs known checksums.
3. `docs/design-decisions.md` §4 names `wiki_pages`/`wiki_links`/`wiki_concepts`; shipped tables are `pages`/`links`. The store crate description advertises "sqlite-vec", which is not a dependency.
4. `docs/okf.md` omits `rule`/`gotcha` kinds from the `kind`→`type` mapping and `generated_by_model` from `generated.by` sources.
5. `docs/ARCHITECTURE.md` says procedural pages have frequency decay; code decays only episodic (`sweep.rs::is_decayable`). `design-memory-aging.md` has stale migration numbers and test paths.
6. `docs/usage.md` says the web UI is read-only; the inbox composer writes messages. `docs/frontend-api.md` documents fewer `/api/v1/search` parameters than `memory_query` supports, so filters like `path_prefix`/`tag` have no HTTP twin.
7. `docs/llm-provider-comparison.md` recommends a local Ollama model as production default; `llm-providers.md` recommends an Anthropic Haiku-class model. Provider and model ids in the comparison predate current defaults.
8. `docs/local-embeddings.md` says both "local is the default" and "local is opt-in for existing installs"; code defaults unset providers to local.
9. `evals/README.md` says four subcommands; five exist. `docs/jev-reranker-adapter.md` references a removed shim.
10. `hooks/_lib.sh` header lists `omp` and omits several agents; the handoff design doc lists `AI_MEMORY_HANDOFF=off` which does not exist.
11. `docs/users.md` says v1 "does not implement RBAC", while per-project grants exist (see [Auth and security](ai-memory-auth-and-security.md)). `docs/design-per-project-authz.md` retains pre-implementation text below its banner. `docs/design-rules-promotion.md` is unimplemented (see [Auto-improvement](ai-memory-auto-improvement.md)).

## Relationships

- Entry point: [ai-memory overview](ai-memory-overview.md).

[^readme]: `../raw/ai-memory/README.md` — "Docs" tables (map of documents), note that dated `design-*`, `research-*`, `issues-*` and `benchmarks/` files are "evidence and design records, not current operating instructions", and the Docker quick-start (placeholder keys).
