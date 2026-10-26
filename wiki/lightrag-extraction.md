---
type: Concept
title: LightRAG knowledge-graph extraction and merge
description: Entity/relation prompts, bounded gleaning, normalization, cache reachability, write-ahead recovery anchors, and merge summarization.
tags: [rag, knowledge-graph, extraction]
status: draft
created: 2026-10-26
generated: { by: llm-wiki-agent/1, at: 2026-10-26T08:55:00Z }
stale_after: 2027-01-24
sources:
  - id: lightrag-aaebfe1
    resource: ../raw/LightRAG/README.md
    scope: ../raw/LightRAG/
    kind: code
    revision: aaebfe1bb8d5
    title: LightRAG repository
---

**Observed:** LightRAG extracts named entities and relations per chunk, normalizes model output, and merges evidence into graph and vector stores with document recovery anchors. Description summarization and source-ID caps bound accumulated graph records. **Synthesis:** the graph is an LLM-mediated compilation of chunk evidence, not a deterministic ground-truth ontology or a validated knowledge base.[^lightrag-aaebfe1]

## Extraction contract

**Observed:** default prompts define eleven entity types plus Other, four-field entity rows and five-field relation rows with explicit delimiters/completion markers. Text-delimited extraction is default; `ENTITY_EXTRACTION_USE_JSON` selects JSON handling. Prompt caps constrain requested output but are not independently measured extraction recall.[^lightrag-aaebfe1]

Gleaning defaults to one additional extraction round; it is skipped with a warning when history exceeds the default 20,480-token input budget. Gleaned duplicates win when their descriptions are longer, not because a separate factual validator proved them better. Normalization handles names and lowercases types, reduces comma-joined types, and drops malformed arity or unsafe/reserved types with warnings. The optional `kg_extraction_validator` runs after model extraction and before merge, ahead of multimodal entity injection.[^lightrag-aaebfe1]

**Observed:** extraction-cache IDs must be attached to the corresponding chunk before cache persistence; failure to attach forfeits that chunk's caching. **Synthesis:** cache reachability matters to later purge/rebuild, not just model-cost optimization.[^lightrag-aaebfe1]

## Merge protocol

1. Flush full-entity/full-relation recovery anchor rows before graph mutation; the durable-anchor callback advances write-state tracking.
2. Merge entities, then relations, using graph and vector updates.
3. Entity vectors use deterministic name-based IDs and name-plus-description content. Relation IDs canonicalize endpoints; vector text includes keywords/endpoints/description.
4. Combine evidence/source IDs and apply configured source caps; KEEP-at-cap can retain the existing relation rather than continually update descriptions.
5. Conditionally summarize accumulated descriptions; record accepted truncation in document metadata.[^lightrag-aaebfe1]

**Observed:** summary handling can join descriptions without another LLM call when both count and token thresholds permit; otherwise it follows a map/reduce-style summarization path. Relation weights combine new-source and stored contributions and are floored against distinct evidence sources. **Synthesis:** weights are compilation arithmetic, not calibrated truth probabilities or relevance scores shared with all retrieval branches.[^lightrag-aaebfe1]

## Failure and maintenance boundaries

**Observed:** anchors precede contribution writes so deletion/recovery can discover partially written work. Graph and vector writes are separate operations; flush errors propagate through the batch completion protocol. Source-ID caps and description truncation mean stored graph prose need not preserve every sentence or every originating chunk indefinitely.[^lightrag-aaebfe1]

## Relationships

- **Depends on:** [Chunks and provenance](lightrag-chunking.md), [model roles](lightrag-models.md), and [storage](lightrag-storage.md).
- **Used by:** [Retrieval](lightrag-retrieval.md) for entity/relation branches.
- **Repaired by:** [Deletion/recovery](lightrag-deletion.md) using anchor and cached-extraction evidence.
- **Related:** [RAG-Anything multimodal grounding](rag-anything-multimodal-grounding.md) relies on LightRAG internals in a different pinned package; API compatibility is not established across revisions.

## Evidence limits

Targeted static prompt, normalization, merge and summarization reads. No extraction outputs, ontology accuracy, hallucination rates, merge concurrency, source-cap recall impact or rollback fault injection was tested. See [coverage](lightrag-source-map.md).

[^lightrag-aaebfe1]: Revision `aaebfe1bb8d5`: `lightrag/prompt.py` entity types and extraction templates; `operate.py::extract_entities, _normalize_and_validate_entity_type, _handle_single_entity_extraction, merge_nodes_and_edges, _merge_nodes_then_upsert, _merge_edges_then_upsert, _handle_entity_relation_summary` (notably 3514–3640, 3994–4409); `lightrag.py::LightRAG.kg_extraction_validator`; `constants.py` gleaning/input/source-cap/summary defaults; `pipeline.py` process-stage flush/terminal status handling.
