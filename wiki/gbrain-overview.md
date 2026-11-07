---
type: Concept
title: GBrain overview
description: What Garry Tan's GBrain agent-memory system is, how its repository is laid out, and where each subsystem is documented in this wiki.
tags: [agent-memory, gbrain, overview]
status: draft
created: 2026-11-06
stale_after: 2027-02-06
generated: { by: llm-wiki-agent/1, at: 2026-11-06T17:00:00Z }
sources:
  - id: readme
    resource: ../raw/gbrain/README.md
    scope: ../raw/gbrain/
    kind: code
    revision: 27f8b9d
    title: GBrain README (repository root)
  - id: version
    resource: ../raw/gbrain/VERSION
    kind: code
    revision: 27f8b9d
    title: GBrain VERSION file
  - id: license
    resource: ../raw/gbrain/LICENSE
    kind: code
    revision: 27f8b9d
    title: GBrain license file
  - id: package-json
    resource: ../raw/gbrain/package.json
    kind: code
    revision: 27f8b9d
    title: GBrain package manifest
  - id: claude-md
    resource: ../raw/gbrain/CLAUDE.md
    kind: code
    revision: 27f8b9d
    title: GBrain CLAUDE.md (operating context for Claude Code)
---

GBrain is a self-hostable, MIT-licensed "memory you control" for AI agents, built by Garry Tan (President and CEO of Y Combinator) to run his own OpenClaw and Hermes agent deployments. It stores explicit facts and Markdown pages with their sources, lets facts be corrected or withdrawn, and exposes the same memory to many agents over a CLI and an MCP server. It starts keyless (keyword retrieval only) and adds semantic search, cited synthesis and background enrichment on demand.[^readme] This page is the entry point to the GBrain cluster of this wiki; every finding is pinned to repository revision `27f8b9d` (submodule `raw/gbrain`, `VERSION` `0.60.593.0`).[^version]

## Identity (Observed)

- **License:** MIT, "Copyright (c) 2026 Garry Tan". The vendored `postgres` driver under `vendor/postgres/` is Unlicense, not MIT (see [testing, CI and release](gbrain-testing-ci-and-release.md)).[^license]
- **Runtime:** TypeScript on Bun ≥ 1.4.4; bin `gbrain` → `src/cli.ts`; library entry `src/core/index.ts`. The README warns that the npm package named `gbrain` is unrelated and that GBrain is installed only from GitHub (`bun install -g github:garrytan/gbrain#latest-stable`) or by clone + `bun link`.[^package-json][^readme]
- **Release cadence:** four-segment versions; the CHANGELOG has 987 `## [` entries (counted by the curator), so the snapshot is one point in a very fast-moving project.[^version]

## What it claims to do (Reported)

- **Brain vs search:** `gbrain search` returns ranked pages; `gbrain think` runs retrieval and then writes a cited answer with an explicit "what the brain doesn't know" gap analysis.[^readme] See [retrieval pipeline](gbrain-retrieval-pipeline.md) and [knowledge graph](gbrain-knowledge-graph.md).
- **Typed knowledge graph** built without LLM calls on trusted local page writes; the README reports relationship-retrieval R@5 rising from 0.6626 to 0.7241 (an external benchmark, not reproduced in this repository; see [evals and benchmarks](gbrain-evals-and-benchmarks.md)).[^readme]
- **Overnight loop:** signal capture → brain-first search → write → auto-link → sync, plus a nightly "dream cycle" (see [dream cycle and autopilot](gbrain-dream-cycle-and-autopilot.md)). The author reports a production brain of 155,795 pages, 24,589 people, 5,340 companies and 66 cron jobs; these are self-reported, undated-in-place figures.[^readme]
- **Company-brain use** with source/operation grants, but the README itself says local files and shared DB credentials are a different trust boundary and the authorization tests are "not a universal no-leak guarantee" (see [authorization and security](gbrain-authorization-and-security.md)).[^readme]

## Setup paths (Reported)

1. Add GBrain to an existing agent (`gbrain setup claude-code|codex`; guides for Grok Bot, Muse, Codex/Claude Code).
2. Publish a local brain over MCP on a Tailscale tailnet (`gbrain mcp expose`, `--funnel` for cloud agents).
3. Connect an existing hosted brain (gbrain.io is optional paid hosting).
4. Standalone CLI: `gbrain init --pglite --no-embedding`, `gbrain import`, `gbrain search`, `gbrain doctor`.
5. Optional new persistent personal agent via `BOOTSTRAP_FOR_AGENTS.md` (see [recipes, plugins and bootstrap](gbrain-recipes-plugins-and-bootstrap.md)).[^readme]

## Architecture in one paragraph (Synthesis of README plus the cluster pages)

Markdown brain repos are synced into a database index (PGLite by default, Postgres + pgvector for shared or large brains) behind one `BrainEngine` contract; one contract-first operation registry generates both the CLI and the MCP tool surface; retrieval fuses vector, keyword, title and relational arms and can walk typed graph edges; background jobs run on a Postgres-native queue ("Minions"); behavior is taught to agents through ~75 Markdown skills rather than code. The README's own architecture diagram shows this flow.[^readme][^claude-md]

## Cluster map

| Question | Page |
| --- | --- |
| What was covered, what was skipped? | [GBrain source map](gbrain-source-map.md) |
| Engines, operation registry, topologies, writers | [Architecture and engines](gbrain-architecture-and-engines.md) |
| Tables, page anatomy, brain vs source, schema packs, size limits | [Data model and system of record](gbrain-data-model-and-system-of-record.md) |
| Search stages, modes, rerank, failure modes | [Retrieval pipeline](gbrain-retrieval-pipeline.md) |
| Embedding defaults, providers, migration, cost caps | [Embeddings and providers](gbrain-embeddings-and-providers.md) |
| Links, typed edges, graph walks, `think` | [Knowledge graph](gbrain-knowledge-graph.md) |
| remember/recall/forget, facts vs takes vs beliefs, core memory | [Memory model](gbrain-memory-model.md) |
| Trust tiers, egress, Memorable, contradiction detection | [Memory trust and egress](gbrain-memory-trust-and-egress.md) |
| CLI dispatch, MCP transports and surfaces, `gbrain setup` | [CLI and MCP surface](gbrain-cli-and-mcp-surface.md) |
| Scopes, grants, what does/doesn't confine callers | [Authorization and security](gbrain-authorization-and-security.md) |
| Job queue | [Minions job queue](gbrain-minions-job-queue.md) |
| Nightly maintenance phases | [Dream cycle and autopilot](gbrain-dream-cycle-and-autopilot.md) |
| Markdown→DB sync, connectors, enrichment, open loops | [Sync and ingestion](gbrain-sync-and-ingestion.md) |
| Skills, resolver, filing rules, skill tooling | [Skills and resolver](gbrain-skills-and-resolver.md) |
| Recipes, plugin lanes, personal-agent bootstrap | [Recipes, plugins and bootstrap](gbrain-recipes-plugins-and-bootstrap.md) |
| Eval suites and reported numbers | [Evals and benchmarks](gbrain-evals-and-benchmarks.md) |
| Tests, CI, releases, vendoring, repo hygiene | [Testing, CI and release](gbrain-testing-ci-and-release.md) |
| Where docs and code disagree | [Doc/code discrepancies](gbrain-doc-code-discrepancies.md) |
| How GBrain compares with other agent-memory systems | [Agent memory landscape survey](agent-memory-landscape-survey.md) |

## Coverage and limits

- **Method:** static inspection only. Seven parallel Explore subagents each read one slice of the repository; the curator then spot-checked a few consequential facts directly (embedding/reranker defaults, skill count of 75, 10 auth scopes, license, 23 `localOnly` operations, CHANGELOG entry count). No code, tests or builds were executed. Findings not spot-checked are subagent observations, not independently re-read by the curator.
- **Large unread areas:** `CHANGELOG.md` (4.8 MB, head only), `TODOS.md` (880 KB, head only), `llms-full.txt`, `docs/eval/system-one/` (887 files), `test/` (7,244 files, organization only), most of `src/core` (588 entries) and `src/commands`. See the [source map](gbrain-source-map.md).
- **Time sensitivity:** defaults, counts and benchmark numbers describe this snapshot only; `stale_after` is set accordingly.

[^readme]: `README.md` intro, "Choose your setup", "Install", "Two ways to query your brain", "Architecture", "License + credit"; the production-brain figures are in the paragraph beginning "I'm Garry Tan".
[^version]: `VERSION` (single line `0.60.593.0`); git revision from `git -C raw/gbrain log -1`.
[^license]: `LICENSE` lines 1–3 ("MIT License", "Copyright (c) 2026 Garry Tan").
[^package-json]: `package.json` `bin.gbrain`, `main`, `engines.bun` (≥ 1.4.4), `exports`.
[^claude-md]: `CLAUDE.md` "Architecture" section (contract-first operations, `BrainEngine`, two engines); read via the architecture subagent.
