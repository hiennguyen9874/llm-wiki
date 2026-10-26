---
type: Concept
title: "RAGFlow knowledge compilation"
description: "Template-driven document compilation and dataset-level merging produce navigable wiki, structure, tree, and mind-map products."
tags: [ml, ragflow, rag]
status: draft
created: 2026-10-26
generated: { by: llm-wiki-agent/1, at: 2026-10-26T08:16:02Z }
stale_after: 2027-01-26
sources:
  - id: ragflow
    resource: ../raw/ragflow/README.md
    scope: ../raw/ragflow/
    kind: code
    revision: 1731e54
    title: RAGFlow repository snapshot
---

# RAGFlow knowledge compilation

**Observed:** knowledge compilation is both a document pipeline component and a dataset-level incremental aggregation system. It turns parsed content into typed products and searchable/navigation projections, rather than merely re-chunking source text. The component dispatches four internal variant families: structure, wiki, tree and mindmap; user-facing template kinds can be more specific.[^ragflow]

## Per-document compilation

`KnowledgeCompilerComponent.Invoke` resolves tenant/dataset scope from canvas globals, treats `kb_id` as dataset identity when needed, and chooses templates by template ID before template-group ID. Variant selection comes from template kind, not an arbitrary DSL variant label. Each template gets isolated config/dependencies; products are stamped with template, kind and variant before conversion to chunk-aligned output.[^ragflow]

| Variant | Inspected mechanism |
| --- | --- |
| Wiki | map extracts → reduce → page planning → refinement → active map state → embedding/merge; incremental and historical dedup helpers |
| Structure | hypergraph entity/relation extraction, row construction, self-loop filtering and evidence-aware merge |
| Tree | RAPTOR-style tree construction and clustering helpers |
| Mindmap | token-budget batches, model JSON retries, shared compiler concurrency |

These are observed control paths; generated content quality and graph fidelity were not measured.[^ragflow]

## Dataset aggregation and lifecycle

Scheduler operations cover publish, dataset locks, claim/ack, progress and cancellation, with MySQL scheduling state and NATS delivery/wake-ups. Consumer processing merges document contributions, handles removal/retraction and scoped page deletion, and updates navigation. Writer contracts persist merged chunks, wiki versions and graph projections. Contribution and dirty-page helpers support incremental updates rather than regenerating every page unconditionally.[^ragflow]

## Retrieval integration

Compilation metadata (`compile_kwd`, `scope_kwd`, template identity and provenance) distinguishes generated products from ordinary chunks. By default, dataset search includes ordinary chunks plus dataset-scoped compiled products while excluding document-scoped ones. Explicit `include_knowledge_compilation=false` excludes all compiled rows; otherwise `knowledge_compilation_scope=all` removes the compilation filter. Agentic retrieval can inject navigation/graph tools when compiled knowledge exists. **Synthesis:** compilation and retrieval must be configured together; the presence of products alone does not prove that a chat request uses them.[^ragflow]

## Relationships

- **Depends on:** [ingestion](ragflow-ingestion.md) and [persistence/queue infrastructure](ragflow-persistence.md).
- **Used by:** [agentic retrieval](ragflow-agent-workflows.md) through compiled-knowledge-aware tools.
- **Related to:** this repository's curator workflow only at the conceptual level; RAGFlow's generated wiki products are not the same governance/provenance contract as this knowledge base.

## Evidence and limits

**Observed** means static inspection, not demonstrated runtime behavior. This page is **draft** because package coverage is sampled; builds, application tests, external services, model execution, and performance claims were not verified. See the [source map](ragflow-source-map.md) for the coverage ledger and redacted security boundary.

[^ragflow]: [RAGFlow source](../raw/ragflow/README.md), revision `1731e54`; locators: `internal/ingestion/component/knowledge_compiler/component.go::KnowledgeCompilerComponent.Invoke / resolveTemplateSpecs / productsToChunkDocs`; `internal/ingestion/component/knowledge_compiler/wiki/wiki.go::Run / run / runMap / runPlan / runRefine`; `internal/ingestion/component/knowledge_compiler/structure/structure.go::Run`; `internal/ingestion/component/knowledge_compiler/structure/compile.go::extractHypergraph / buildRows / filterSelfLoopRelations`; `internal/ingestion/component/knowledge_compiler/tree/raptor.go::Run / buildTree`; `internal/ingestion/component/knowledge_compiler/mindmap/mindmap.go::Run`; `internal/ingestion/knowledge_compile/scheduler.go::Publish / WithDatasetLock / Claim / Ack / CancelInflight`; `internal/ingestion/knowledge_compile/consumer.go::processBatch / mergeWikiProductsBySlug / deleteMissingScopedWikiPages`; `internal/ingestion/knowledge_compile/writer.go::Writer / engineWriter.WriteMerged`; `internal/ingestion/knowledge_compile/wiki_contribution.go::prepareWikiContributionDiff / commitWikiContributions`; `internal/service/dataset/search.go::knowledgeCompilationFilter`; `internal/agentic_rag/compiled_knowledge.go::compiledKnowledgeTools`.
