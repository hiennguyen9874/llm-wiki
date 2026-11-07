---
type: Concept
title: ai-memory retrieval pipeline
description: How memory_query fuses FTS, entity, vector, graph and observation streams with RRF, applies filters, authority adjustments and optional answer synthesis.
tags: [agent-memory, ai-memory, retrieval, search, rrf]
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
  - id: store-reader
    resource: ../raw/ai-memory/crates/ai-memory-store/src/reader.rs
    scope: ../raw/ai-memory/
    kind: code
    revision: 26fa9cf
    title: ai-memory-store reader.rs (ranking)
  - id: mcp-server
    resource: ../raw/ai-memory/crates/ai-memory-mcp/src/server.rs
    scope: ../raw/ai-memory/
    kind: code
    revision: 26fa9cf
    title: ai-memory-mcp server.rs (memory_query, answer)
  - id: usage
    resource: ../raw/ai-memory/docs/usage.md
    scope: ../raw/ai-memory/
    kind: code
    revision: 26fa9cf
    title: Usage guide
---

# ai-memory retrieval pipeline

Retrieval over the markdown wiki is a **reciprocal-rank fusion (RRF)** of several candidate streams, narrowed by filters and nudged by bounded "authority" factors. The zero-LLM path is `memory_query` → optional query embedding → `hybrid_search_scopes` → post-fusion authority → optional rerank → optional answer.[^store-reader][^mcp-server]

Evidence class: **Observed** (static inspection of `reader.rs` and `server.rs`, delegated); line numbers reported by the inspector were approximate and are not recorded. Nothing executed. Ranking *quality* claims live in [Evals and benchmarks](ai-memory-evals-and-benchmarks.md) and are **Reported**.

## Streams and fusion

`score = Σ 1/(k+rank_i)` with `k = 60`; hits carry `rank = -score`.[^store-reader] Streams (`streams_active`): 
- **fts** — `pages_fts` over latest, non-expired versions.
- **entity** — entity-match candidates.
- **vector** — page embeddings for the configured `(provider, model, dim)`; skipped without a query vector.
- **abstract** — optional L0 abstract embeddings, off by default.
- **graph** — link-neighbour expansion seeded only from fts/vector/entity seeds.
- **observation** — on by default; each matching observation votes once for its session's latest `sessions/<id>.md` page, and a voted session page loses its page-FTS contribution to avoid double counting.[^store-reader][^readme]

CJK text: an auxiliary bigram index (`pages_cjk_fts`) lets zero-LLM search match unspaced Han/Kana/Hangul substrings.[^store-reader][^readme]

## Filters

`PageFilter { kind, tier, path_prefix, tag }` is applied inside every stream's SQL *before* ranking, so a rare kind cannot be crowded out; `path_prefix` is a literal LIKE-escaped prefix, `tag` matches frontmatter tags case-insensitively.[^store-reader][^usage]

## Authority adjustment

A bounded multiplier clamped to **[0.55, 1.50]**: kind (`rule`/`decision` +0.15 … `session` −0.15), tier (semantic/procedural +0.10, episodic −0.08, working −0.03), `pinned` +0.08, `_lint/` −0.20, `investigations/` −0.05, and tags (`canonical`/`source-of-truth` +0.20, `active` +0.05; caps for `do-not-answer-from`/`test-fixture` 0.55, `superseded` 0.65, `historical` 0.80). Optional factors — session-recall routing, belief authority, feedback demotion, query-signal weight — default to off/0.0.[^store-reader]

## Special modes

- **`as_of`** — entity timeline + version-filtered FTS only; excludes vector, graph, raw fallback, rerank and access bumps; rejects `global`/`scopes` (see [Wiki storage](ai-memory-wiki-storage-and-okf.md)).[^store-reader]
- **`global=true`** — a distinct FTS-only, viewer-filtered ranker.[^store-reader]
- **`explain=true`** — per-stream ranks, RRF contributions, authority and timings (`fts_ms`, `entity_ms`, `vector_ms`, `graph_ms`, `observation_ms`, `rerank_ms`).[^store-reader]
- Single-project searches also union reserved `_global` scope hits and optionally profile-scope hits.[^mcp-server]

## `query_answer` synthesis (opt-in)

With `answer=true` **and** a `QueryAnswer` LLM provider configured, the server builds a numbered evidence context, uses a system prompt forbidding outside knowledge, requires structured output, and rejects the answer if any citation is unknown or ambiguous. With `[query_answer] max_context_tokens` set, budgeting uses 1 UTF-8 byte ≈ 1 token, a 1024-token envelope reserve, whole-snippet admission first and at most one sentence-safe fragment, with omission counts reported; retrieval hits are never truncated. Not supported with `global` or `as_of`. Without a provider the response carries `answer_unavailable`, not an error.[^mcp-server]

## Relationships

- Indexes come from [Architecture](ai-memory-architecture.md); tools in [MCP tools and HTTP surfaces](ai-memory-mcp-tools-and-http-surfaces.md).
- Embeddings: [LLM and embedding providers](ai-memory-llm-and-embedding-providers.md).
- HTTP `/api/v1/search` is *not* feature-equivalent to `memory_query` — see [Source map and discrepancies](ai-memory-source-map-and-doc-discrepancies.md).

[^readme]: `../raw/ai-memory/README.md` — "Architecture" (retrieval stream list), "Everyday use" (filters, CJK).
[^store-reader]: `../raw/ai-memory/crates/ai-memory-store/src/reader.rs::hybrid_search_inner, active_streams, PageFilter, PageAuthority::from_stored, search_pages_for_project_at_filtered, SearchExplain, StreamTimings`; `src/fts_query.rs::cjk_index_terms, prepare_cjk_fts5_query`; `src/retrieval_tuning.rs`.
[^mcp-server]: `../raw/ai-memory/crates/ai-memory-mcp/src/server.rs::QueryArgs, ReasoningTier, prepare_answer_request, validate_answer_citations, ANSWER_SYSTEM_PROMPT, global_scope_hits`.
[^usage]: `../raw/ai-memory/docs/usage.md` — `memory_query` filter documentation (path_prefix, tag, kind, tier).
