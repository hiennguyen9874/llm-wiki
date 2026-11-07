---
type: Concept
title: GBrain knowledge graph and think
description: How GBrain extracts typed links without LLM calls, walks them breadth-first, uses them in retrieval and ranking, and how the think verb synthesizes cited answers.
tags: [agent-memory, gbrain, knowledge-graph, think]
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
  - id: retrieval-doc
    resource: ../raw/gbrain/docs/architecture/RETRIEVAL.md
    kind: code
    revision: 27f8b9d
    title: Retrieval architecture
  - id: multi-hop
    resource: ../raw/gbrain/docs/guides/multi-hop.md
    kind: code
    revision: 27f8b9d
    title: Multi-hop guide
  - id: graph-ranking
    resource: ../raw/gbrain/docs/guides/graph-ranking.md
    kind: code
    revision: 27f8b9d
    title: Graph ranking guide
  - id: entity-recall
    resource: ../raw/gbrain/docs/guides/entity-recall.md
    kind: code
    revision: 27f8b9d
    title: Entity recall guide
  - id: think-gather
    resource: ../raw/gbrain/src/core/think/gather.ts
    kind: code
    revision: 27f8b9d
    title: think gather stage
  - id: memory-boundaries
    resource: ../raw/gbrain/docs/guides/memory-boundaries.md
    kind: code
    revision: 27f8b9d
    title: Memory boundaries
---

GBrain keeps a typed edge graph alongside text retrieval. The README's rationale: vector search finds similar text, graph retrieval follows stored relationships, and extracted edges are *evidence to inspect, not proof* a relationship is true.[^readme] Edges are extracted without any LLM call on trusted local writes, walked breadth-first, and used both as a retrieval arm and as ranking signals. The `think` verb adds multi-stream gathering and cited synthesis on top. See [retrieval pipeline](gbrain-retrieval-pipeline.md) for the surrounding stages.

## Extraction (Reported unless noted)

- **Auto-link** runs on the write path only for **trusted local** `put_page`. Remote `put_page` (including stdio MCP) skips inline extraction; its edges arrive later via startup/idle sweeps, `gbrain extract links --source db`, a post-commit `mentions` effect or explicit `add_link`. The README says the same.[^retrieval-doc][^memory-boundaries][^readme]
- It recognizes Markdown links, Obsidian `[[wikilink|alias]]`, and typed-link blockquotes (`> **Convention:** …`), batch-inserted through `addLinksBatch`. Link types (`attended`, `works_at`, `invested_in`, `founded`, `advises`) are inferred heuristically from sentence context.[^retrieval-doc]
- **Entity recall** additionally links by page title, record-title subject, `aliases:` frontmatter and declared codes, keyless.[^entity-recall]
- A separate NER pass (`extract-ner.ts`, per the sync subagent) reuses a gazetteer and schema-pack `link_types[].inference.regex` to emit `typed_ner` edges without overwriting plain mentions (Observed by subagent).

## Traversal and ranking

- **Breadth-first walks** since v0.60.294.0: one recursive CTE (`bfsWalkCtes` in `engine-sql/links.ts`), each page visited once at shortest distance, a cap on visited pages (20,000) rather than routes, and a 5,000-row result cap. Path weight is the product of intermediate hub weights; degree saturates at 300 link rows. Reported speedups: a depth-5 12-page clique from 44–91 ms to 4–9 ms (medians against v0.60.292.0).[^retrieval-doc]
- **Multi-hop relationship chains:** vocabulary `founded`, `invested_in` (with `led_round`), `advises`, `works_at`, `attended`, `yc_partner`, plus `mentions`. Executor bounds: ≤ 50 frontier pages, 100 edges/page, 10 retained paths/page. The planner refuses coordination, negation, time constraints, counting, quoted names and multi-entity questions (Observed by subagent in `relational-chain.ts` and `relational-plan.ts`).[^multi-hop]
- **Ranking policy:** link type `amends` is excluded from all ranking readers (`NON_RANKING_LINK_TYPES`). `rank_entities` counts distinct `(from,to,link_type)` edges, folds redirect stubs up to 5 hops and has a 15 s Postgres deadline.[^graph-ranking]
- Benchmark claim: relationship questions improve mean R@5 from 0.6626 to 0.7241 with graph retrieval; `graph-oracle-parse` at 0.9791 is an upper bound, not a product score (Reported; see [evals](gbrain-evals-and-benchmarks.md)).[^readme]

## think (Observed by subagent in code)

`gbrain think` = intent → gather → synthesize → optional commit. Gather runs five streams: pages (keyword + vector), takes (keyword + vector), a graph walk (`traversePaths(anchor, {depth: graphDepth ?? 2, direction: 'both'})`, only when `--anchor` is given) and anchor-page hydration; a graph-walk failure is logged and yields an empty stream rather than failing. The answer carries citations and an explicit gap analysis (stale pages, uncited claims, contradictions, holes) per the README. Only `think` is documented to escalate from CRAG (`search.crag_think`).[^think-gather][^readme]

## Relationships

- Depends on: [data model](gbrain-data-model-and-system-of-record.md) (`links` table), [memory model](gbrain-memory-model.md) (takes and facts feed `think`).
- Part of: [retrieval pipeline](gbrain-retrieval-pipeline.md) and [GBrain overview](gbrain-overview.md).

[^readme]: `README.md` intro bullets ("A typed knowledge graph"), "Architecture" ("Why the graph matters"), "Two ways to query your brain".
[^retrieval-doc]: `docs/architecture/RETRIEVAL.md` "Auto-link", "Breadth-first graph walks", "Multi-hop relationship chains", "The benchmark".
[^multi-hop]: `docs/guides/multi-hop.md` (chain vocabulary); bounds from `src/core/search/relational-chain.ts` and `read-enrichment.ts` via subagent.
[^graph-ranking]: `docs/guides/graph-ranking.md`; `src/core/link-ranking-policy.ts`.
[^entity-recall]: `docs/guides/entity-recall.md`.
[^think-gather]: `src/core/think/gather.ts` lines 8, 40–47, 134, 241–259.
[^memory-boundaries]: `docs/guides/memory-boundaries.md` "Page writes and the graph are separate outcomes".
