---
type: Concept
title: Hindsight retain pipeline
description: How Hindsight turns input content into extracted facts, entities and graph links, including chunking, extraction modes, delta retain and attachments.
tags: [agent-memory, hindsight, retain, ingestion]
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
  - id: retain-doc
    resource: ../raw/hindsight/hindsight-docs/docs/developer/retain.md
    kind: documentation
    revision: eb963cb
    title: Retain developer doc
  - id: engine
    resource: ../raw/hindsight/hindsight-api-slim/hindsight_api/engine/retain/orchestrator.py
    kind: code
    revision: eb963cb
    title: Retain orchestrator
---

`retain` is Hindsight's write path: an LLM extracts structured facts, temporal data, entities and relationships from submitted content, which are normalized into canonical entities, time series and search indexes inside a [bank](hindsight-memory-banks.md).[^readme] It feeds both [recall](hindsight-recall-pipeline.md) and, asynchronously, [consolidation](hindsight-consolidation-and-mental-models.md).[^retain-doc]

## Behaviour (Reported by docs)

- **Fact types:** `experience` (the bank's own agent, first person) vs `world` (everyone else); decided by who is speaking and steerable with each item's `context`. Facts carry emotions/reasoning, not raw text.[^retain-doc]
- **Entities:** resolved by fuzzy name matching plus co-occurrence/temporal proximity. `entity_labels` give a controlled `key:value` vocabulary that resolves by exact match only and is never fuzzy-merged.[^retain-doc]
- **Graph:** four link kinds — entity, time-based, meaning-based (semantic), causal (`HINDSIGHT_API_RETAIN_EXTRACT_CAUSAL_LINKS`, default `true`). Two time dimensions: when it happened vs when it was learned.[^retain-doc]
- **Extraction modes:** `concise` (default), `verbose`, `custom`, `verbatim`, `chunks`; `retain_mission` steers but does not replace the rules and is ignored in `chunks` mode. A mission that excludes everything yields `memory_unit_count: 0` while retain still succeeds; recover with `POST .../documents/{id}/reprocess`.[^retain-doc]
- **Attachments:** `content` may be an ordered list of text/image/file blocks; `HINDSIGHT_API_VLM_MODEL` is a vision-only slot, a non-vision model returns 422, and batch retain (`HINDSIGHT_API_RETAIN_BATCH_ENABLED`) cannot carry attachments (422).[^retain-doc]
- Consolidation is triggered asynchronously after retain.[^retain-doc]

## Implementation (Observed)

Order of work in `retain_batch`: writability/bank-alive checks → embeddings reachability precheck → build contents → chunk → delta decision → fact extraction → entity resolution → storage → link creation.[^engine]

| Stage | Where | Notes |
| --- | --- | --- |
| Chunking | `engine/retain/fact_extraction.py::iter_chunks`, `chunk_text` | Conversation arrays, JSONL, image-aware, else recursive sentence splits; default `HINDSIGHT_API_RETAIN_CHUNK_SIZE=3000` chars |
| Extraction | `extract_facts_from_contents`, `extract_facts_from_contents_batch_api` (LLM Batch API) | Schemas `Fact`, `CausalRelation`, `ExtractedFact`, `VerbatimExtractedFact`; `HINDSIGHT_API_RETAIN_EXTRACTION_MODE`, `RETAIN_MAX_COMPLETION_TOKENS=64000` |
| Entity resolution | `engine/memories/pg/entity_resolver.py::EntityResolver.resolve_entities_batch` | `HINDSIGHT_API_RETAIN_ENTITY_LOOKUP` = `full` or `trigram` (default `trigram`); Oracle fuzzy variant |
| Links | `engine/retain/link_creation.py` (`create_temporal_links_batch`, `create_semantic_links_batch`, `create_causal_links_batch`) | Semantic link threshold 0.7, top-k 50; causal links store only canonical `caused_by` |
| Delta retain | `_try_delta_retain`, `_classify_chunk_diff`, `_delta_metadata_only` | Re-retaining a document diffs chunks; unchanged chunks keep existing facts, entities and links |

Entry points: `MemoryEngine.retain_batch_async` / `retain_async` in `engine/memory_engine.py`; queued work runs through the `async_operations` table (see [API surface](hindsight-api-surface.md)).[^engine]

## Relationships

- Feeds: [Recall pipeline](hindsight-recall-pipeline.md), [Consolidation and mental models](hindsight-consolidation-and-mental-models.md).
- Guarded by: [Memory defense](hindsight-extensions-defense-webhooks.md) (redact/block secrets before storage).
- Uses: [LLM providers](hindsight-llm-embedding-providers.md) for extraction and embeddings.

## Limits

Evidence class: docs claims are Reported; the pipeline table is Observed by subagent static inspection (line numbers omitted because they drift). Extraction quality varies by LLM; see retain capability pass rates in [benchmarks and testing](hindsight-benchmarks-and-testing.md). Not executed.

[^readme]: `README.md` § "The Three Operations" → Retain.
[^retain-doc]: `hindsight-docs/docs/developer/retain.md` (fact types, entities, links, extraction modes, attachments sections).
[^engine]: `hindsight-api-slim/hindsight_api/engine/retain/orchestrator.py::retain_batch`, `engine/retain/fact_extraction.py`, `engine/retain/link_creation.py`, `engine/memories/pg/entity_resolver.py`, `engine/memory_engine.py::retain_batch_async`.
