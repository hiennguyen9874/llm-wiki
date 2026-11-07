---
type: Concept
title: Hy Memory and MemHub overview
description: Entry-point map of the Tencent Hunyuan Hy-Memory monorepo — the hy-memory Python SDK (chat, working, coding scenes) and the MemHub local-first product built on it.
tags: [agent-memory, hy-memory, memhub, overview]
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

# Hy Memory and MemHub overview

Hy Memory is a "production-grade dual-system cognitive memory" engine and Python SDK (`hy-memory`) for self-evolving LLM agents, with specialised pipelines for three task scenes: hierarchical long-term memory for **chat**, a two-layer fact + reusable-experience memory for **working**, and the same two layers plus a version-evolution diff chain for **coding** (`README.md::Hy Memory intro`, `System Architecture`).[^hy-memory] **MemHub** is a local-first desktop + CLI product built on the SDK that unifies conversations and coding traces from user-authorised AI apps (Claude Code, Cursor, Codex, OpenCode, Qwen Code …) into one managed runtime and data directory (`README.md::Hy Memory intro`; `memhub/README.md`).[^hy-memory] This page is the navigation hub; details live in the linked concepts.

## Scenes and modes

| `scene` | Tasks | Memory shape | Detail |
|---|---|---|---|
| `chat` | small talk, personal info, preferences | hierarchy L0–L7 | [Chat hierarchy and write path](hy-memory-chat-hierarchy-and-write-path.md), [Chat retrieval](hy-memory-chat-retrieval-pipeline.md) |
| `working` | productivity work (docs, research, computer use) | facts + experiences | [Working and coding memory](hy-memory-working-coding-memory.md) |
| `coding` | software engineering | same two layers + diff chain | [Diff chain](hy-memory-coding-diff-chain.md) |

(`README.md::System Architecture` table.)[^hy-memory]

Modes: `lite` (raw-only embedding, no LLM, no graph), `pro` (LLM extraction + reconcile, graph optional), `ultra` (adds System 2 schema induction and the cross-domain sweeper, graph always on, triggered explicitly by `evolve()`) (`README.md::Chat: Memory Hierarchy / Modes`).[^hy-memory] Working/coding writes need a tool-call trace and only take effect in `pro`/`ultra`; `lite` stores everything as raw (`README.md::Working & Coding Memory`).[^hy-memory]

## Map of the knowledge base

- SDK: [API and config](hy-memory-sdk-api-and-config.md) · [storage and re-embedding](hy-memory-storage-and-reembed.md) · [runtime, concurrency, observability](hy-memory-runtime-concurrency-and-observability.md) · [System 2 evolution](hy-memory-system2-evolution.md)
- Research: [CMB benchmark](cmb-coding-memory-benchmark.md)
- MemHub: [product architecture](memhub-product-architecture.md) · [modes and write queue](memhub-memory-modes-and-write-queue.md) · [import adapters and live sync](memhub-import-adapters-and-live-sync.md) · [embedding switching](memhub-embedding-space-switching.md) · [privacy and permissions](memhub-privacy-and-permissions.md) · [apps and packages](memhub-apps-and-packages.md) · [host bridge](memhub-host-bridge-harness-integration.md)
- Integrations and project: [OpenClaw and Hermes plugins](hy-memory-plugins-openclaw-hermes.md) · [releases, CI, quality](hy-memory-release-ci-and-quality.md)

## Papers and releases claimed by the README

The README lists three papers: the dual-process cognitive memory system (EMNLP 2026, arXiv 2606.09483; 8-layer hierarchy with reconciliation and cross-domain schema induction), the CMB coding benchmark (ICLR 2027 submission, PDF in `docs/papers/`), and the Hy-Memory-30B-A3B technical report on attributed RL for memory writing (arXiv 2610.22196) (`README.md::Papers`).[^hy-memory] Only the CMB PDF is in the repository; the other two are linked, not read (evidence class: Reported). News entries cite MemHub v1.0.4–v1.0.6, Hy Memory 2.0, FP8/GGUF model releases (`README.md::Latest News`, Reported).[^hy-memory]

Supported install matrix: core includes ChromaDB and Kuzu; extras add Qdrant, FAISS, Neo4j, MySQL cache, local cross-encoder rerank (`README.md::Quick Start §1`; `pyproject.toml`).[^hy-memory] Licence: Apache-2.0 (`README.md::License`).[^hy-memory]

## Relationships

- Contains: [MemHub product architecture](memhub-product-architecture.md) (product layer on the SDK).
- Documented by: [SDK API and config](hy-memory-sdk-api-and-config.md).

## Coverage and limits

Compiled from read-only static inspection delegated to six exploration subagents over the repo (~1,819 files); no code was executed and no tests were run. Slices: SDK core, chat pipelines, working/coding, MemHub core + contracts, MemHub apps/packages + harness docs, plugins/CI/meta. Not individually read: most per-language prompt modules, individual tests, `web` component internals, lockfiles, SBOM, and `site` assets (excluded as generated/decorative or low-yield). `README.zh.md` is the Chinese twin of the README and was not separately compared. The README states install pins `2.0.4` while `pyproject.toml` is `2.0.14`, so quick-start pins are stale (Observed).[^hy-memory]

[^hy-memory]: Hy-Memory monorepo, revision 9737431 (`hy-memory` 2.0.14 per `pyproject.toml`; MemHub 1.0.6 per `memhub/README.md`). Locators are given inline per claim as `path::section-or-symbol`. Evidence class is Observed (static inspection delegated to read-only subagents, unexecuted) unless a claim is labelled Reported, Synthesis, or Unverified.
