---
type: Concept
title: Ragas synthetic-test knowledge graph
description: Length-dependent transforms build document/chunk property graphs whose summary and entity relationships feed query synthesis.
tags: [rag, synthetic-data, knowledge-graph, ingestion]
status: draft
created: 2026-10-26
generated: { by: llm-wiki-agent/1, at: 2026-10-26T09:28:37Z }
stale_after: 2027-01-24
sources:
  - id: ragas-298b682
    resource: ../raw/ragas/README.md
    scope: ../raw/ragas/
    kind: code
    revision: 298b682
    title: Ragas repository
---

**Observed:** Ragas' synthetic-data graph consists of document/chunk nodes with property dictionaries and typed relationships; entities and themes normally live as properties, not dedicated entity vertices. Sequential/parallel transformation plans populate summaries, embeddings, themes, entities and relationships that query synthesizers consume. **Synthesis:** this is a test-generation context graph, not evidence of an application-serving graph database.[^ragas-298b682]

## Corpus-dependent default pipeline

`default_transforms` bins document token lengths as 0–100, 101–500 and 501+. If at least 25% are in the long bin, it selects headline extraction/splitting, summaries and a question-potential filter, then parallel embedding/theme/entity extraction and cosine/entity-overlap relations. Otherwise a >=25% medium-bin branch uses a no-splitting document-oriented pipeline. If neither branch qualifies, it raises the short-document error. Prechunked input gets a separate splitter-free transform policy.[^ragas-298b682]

| Property or relationship | Producer / consumer significance |
| --- | --- |
| `page_content` / `document_metadata` | Input corpus data; headline-created chunks do not simply copy all parent metadata |
| `summary` / `summary_embedding` | Summary and embedding extractors; persona generation and similarity links |
| `themes` / `entities` | LLM extractors; scenario concept/persona matching |
| `summary_similarity` | Default cosine builder, threshold 0.7 long/prechunked vs 0.5 medium; abstract multi-hop |
| `entities_overlap` / `overlapped_items` | Overlap builder; specific multi-hop requires this vocabulary |
| `child` / `next` | Splitter provenance/order edges; parent lookup and chunk substitution |

CustomNodeFilter scores question potential on a 1–5 rubric, drops scores <=2 and retains nodes lacking summary context with a warning. Summary extraction uses the first token-limited segment; not every extractor processes long content identically. **Synthesis:** length mix, splitting success and property availability can skew which corpus material becomes candidate scenarios; actual yield was not measured.[^ragas-298b682]

## Mutation, persistence and reproducibility

Transform lists run sequentially; Parallel stages execute plans concurrently under configured worker limits. Execution plans mutate the graph; KnowledgeGraph.add appends nodes/relationships without an existence check, and rollback_transforms raises NotImplementedError. **Synthesis:** repeated or overlapping transform runs can append duplicate edges; the graph does not enforce transform idempotency. Avoid mixing property producers and consumers in one custom parallel stage without dependency ordering.[^ragas-298b682]

KnowledgeGraph saves JSON with UUID identifiers, full properties and relationship endpoint references; load reconnects nodes by ID. There is no explicit format version. A rebuild obtains new UUIDs, and raw corpus/embedding properties may remain in persisted graph files. Version and protect those artifacts independently of published evaluation results.[^ragas-298b682]

## Relationships and limits

- Supplies property/edge vocabulary to [query synthesis](ragas-testset-generation.md).
- Uses [models and embeddings](ragas-model-adapters.md) and [prompt lifecycle](ragas-prompt-optimization.md).
- Conceptual KG/scenario diagrams were visually inspected, not treated as proof of exact defaults. No graph generation, transform rerun, persistence round trip, token count or model-quality check executed.

[^ragas-298b682]: Ragas `298b682`, `src/ragas/testset/graph.py::Node/Relationship/KnowledgeGraph.save/load/_add_relationship`; `src/ragas/testset/transforms/default.py::default_transforms/default_transforms_for_prechunked`; `transforms/engine.py::apply_transforms/Parallel/rollback_transforms`; `transforms/filters.py::CustomNodeFilter`; `transforms/extractors/llm_based.py::SummaryExtractor`; `transforms/splitters/headline.py::HeadlineSplitter`; `transforms/relationship_builders/cosine.py::CosineSimilarityBuilder`; `transforms/relationship_builders/traditional.py::OverlapScoreBuilder` (transform paths relative to `src/ragas/testset/`); `docs/_static/imgs/kg_rag.png` (whole diagram). Static inspection only unless explicitly stated otherwise; coverage and remaining limits: [source map](ragas-source-map.md).
