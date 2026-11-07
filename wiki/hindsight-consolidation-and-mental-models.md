---
type: Concept
title: Hindsight consolidation, observations, mental models and knowledge pages
description: How Hindsight consolidates facts into evidence-backed observations and maintains mental models and knowledge pages as living, auto-refreshed synthesis.
tags: [agent-memory, hindsight, consolidation, mental-models, knowledge-pages]
status: stable
created: 2026-11-06
generated: { by: llm-wiki-agent/1, at: 2026-11-06T16:50:00Z }
sources:
  - id: readme
    resource: ../raw/hindsight/README.md
    scope: ../raw/hindsight/
    kind: code
    revision: eb963cb
    title: Hindsight README (monorepo root)
  - id: observations-doc
    resource: ../raw/hindsight/hindsight-docs/docs/developer/observations.mdx
    kind: documentation
    revision: eb963cb
    title: Observations developer doc
  - id: mental-models-doc
    resource: ../raw/hindsight/hindsight-docs/docs/developer/mental-models.mdx
    kind: documentation
    revision: eb963cb
    title: Mental models developer doc
  - id: pages-doc
    resource: ../raw/hindsight/hindsight-docs/docs/developer/knowledge-pages.mdx
    kind: documentation
    revision: eb963cb
    title: Knowledge pages developer doc
  - id: consolidator
    resource: ../raw/hindsight/hindsight-api-slim/hindsight_api/engine/consolidation/consolidator.py
    kind: code
    revision: eb963cb
    title: Consolidation job
---

Retained facts do not stay a flat pile: a background consolidation job merges related facts into **observations**; **mental models** are standing answers to a fixed question that rewrite themselves as the bank learns; **knowledge pages** are mental models with sensible defaults, organized in a folder tree and projectable to disk as Markdown.[^readme]

## Observations

- Deduplicated, evidence-grounded beliefs with proof count and exact quotes; *refined, never overwritten* — history is preserved, so new evidence strengthens, weakens or extends a belief.[^observations-doc]
- Auto-consolidation runs after retain/delete/update; disable with `HINDSIGHT_API_ENABLE_AUTO_CONSOLIDATION=false` (code default on).[^observations-doc][^consolidator]
- Near-duplicate reconciliation at cosine ≥ `HINDSIGHT_API_CONSOLIDATION_DEDUP_THRESHOLD` (default 0.97), PostgreSQL only, skipped on Oracle.[^observations-doc]
- Scopes default `combined`; also `per_tag`, `all_combinations`, `shared`, explicit lists. `consolidation_strategies` give per-scope missions/caps; first matching strategy wins whole.[^observations-doc]
- Stored in `memory_units` with `fact_type="observation"`; job in `engine/consolidation/consolidator.py::run_consolidation_job`, triage in `consolidation/triage.py` (Observed).[^consolidator]
- Defaults: `CONSOLIDATION_BATCH_SIZE=50`, `CONSOLIDATION_LLM_BATCH_SIZE=8`.[^observations-doc]

## Mental models

- A saved reflect answer for one standing question; reading one is a DB read (no retrieval, no LLM).[^mental-models-doc][^readme]
- Trigger defaults: `mode: "full"` (or `delta`), `refresh_after_consolidation: false`, `refresh_cron: null` (mutually exclusive with post-consolidation refresh), `fact_types: null` (all), `exclude_mental_models: false`.[^mental-models-doc]
- History capped at 50 rows (`HINDSIGHT_API_MENTAL_MODEL_HISTORY_MAX_ENTRIES`); a failed refresh pauses automatic refreshes until a manual success; delta gate allows at most 200 new memories (`..._DELTA_GATE_MAX_MEMORIES`).[^mental-models-doc]
- Code: `engine/mental_model_refresh.py`, `engine/reflect/delta_ops.py`, `retractions.py`, `structured_doc.py` (Observed).[^consolidator]

## Knowledge pages

- A mental model with defaults pre-chosen: built from observations, `mode: delta`, `exclude_mental_models: true`, `refresh_after_consolidation: true`, larger content budget.[^pages-doc]
- Pages live in folders; `hindsight fs mount --bank <id>` projects them as Markdown; page search is document-level (full-text + semantic fused, no reranking); pages are a *projected view* — deleting one loses nothing.[^pages-doc]
- Rendered by `engine/page_markdown.py` with YAML frontmatter; table `knowledge_pages`; routes `/knowledge-base/*` (Observed).[^consolidator]

## Efficiency claims (Reported, vendor)

Decision-model triage cuts consolidation LLM calls ~40% at the same pass rate; a 20-memory page refresh drops from 3 to 1 LLM calls and ~70% fewer input tokens. See [Decision models](hindsight-decision-models.md).[^observations-doc][^pages-doc]

## Relationships

- Inputs from [Retain](hindsight-retain-pipeline.md); outputs consumed by [Recall](hindsight-recall-pipeline.md) and [Reflect](hindsight-reflect-agent.md).
- Seeded for repos by [Coding agents](hindsight-coding-agents.md) (five knowledge pages per repo).
- Webhook `consolidation.completed` is emitted ([Extensions, defense, webhooks](hindsight-extensions-defense-webhooks.md)).

[^readme]: `README.md` § "Observations", "Mental Models & Knowledge Pages".
[^observations-doc]: `hindsight-docs/docs/developer/observations.mdx` (consolidation, scopes, dedup, triage sections).
[^mental-models-doc]: `hindsight-docs/docs/developer/mental-models.mdx` and `api/mental-models.mdx` (trigger, history, delta gate).
[^pages-doc]: `hindsight-docs/docs/developer/knowledge-pages.mdx` (defaults, fs mount, search, refresh cost).
[^consolidator]: `hindsight-api-slim/hindsight_api/engine/consolidation/{consolidator,triage}.py`, `engine/mental_model_refresh.py`, `engine/page_markdown.py`, `config.py::DEFAULT_ENABLE_AUTO_CONSOLIDATION`.
