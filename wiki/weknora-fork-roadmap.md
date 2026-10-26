---
type: Synthesis
title: WeKnora selective fork and feature adoption roadmap
description: A baseline-first fork strategy preserves WeKnora's existing mechanisms and selectively adopts document, retrieval, permission, sync and recovery designs from other RAG systems.
tags: [rag, weknora, architecture, synthesis, roadmap]
status: draft
created: 2026-10-26
generated: { by: llm-wiki-agent/1, at: 2026-10-26T16:19:21Z }
stale_after: 2027-01-26
sources:
  - id: weknora
    resource: ../raw/WeKnora/README.md
    scope: ../raw/WeKnora/
    kind: code
    revision: fd7a2586fd58
    title: WeKnora v0.8.3 repository snapshot
  - id: ragflow
    resource: ../raw/ragflow/README.md
    scope: ../raw/ragflow/
    kind: code
    revision: 1731e54b3aa0
    title: RAGFlow repository snapshot
  - id: openrag-repo
    resource: ../raw/openrag/README.md
    scope: ../raw/openrag/
    kind: code
    revision: 6fc819d3ec10
    title: OpenRAG repository
  - id: lightrag-aaebfe1
    resource: ../raw/LightRAG/README.md
    scope: ../raw/LightRAG/
    kind: code
    revision: aaebfe1bb8d5
    title: LightRAG repository
  - id: txtai-repo
    resource: ../raw/txtai/README.md
    scope: ../raw/txtai/
    kind: code
    revision: 738aac498ccb
    title: txtai repository
  - id: ragas-298b682
    resource: ../raw/ragas/README.md
    scope: ../raw/ragas/
    kind: code
    revision: 298b68274234
    title: Ragas repository
---

**Synthesis / proposed engineering decision:** use WeKnora as the application control plane, retain its existing RAG/agent/wiki mechanisms, and adopt narrow algorithms and lifecycle contracts rather than integrating several full RAG runtimes. Its Go/Dig modular monolith and Python parsing boundary are suitable extension seams, but not a guarantee that arbitrary features plug in without core changes. Prioritize measured document/retrieval failures and security invariants before adding graph modes or extra databases. This roadmap is not an implemented fork or a demonstrated quality improvement.[^weknora]

## Correct the starting assumptions

- WeKnora already has [original-chunk citation sources and a request-local source registry](weknora-citations-source-boundary.md), plus an explicit untrusted-source prompt. Do not import RAGFlow's entire evidence registry or claim a source boundary is absent.[^weknora]
- [Datasource sync](weknora-datasource-sync.md) already persists streaming cursors through the repository. The inspected implementation continues on individual ingest failures and exposes partial outcomes; deletion failures normally wait for full sync. Improve failed-item recovery rather than replace synchronization wholesale.[^weknora]
- Document deletion already invokes graph cleanup by document/KB namespaces. Correct rebuilding of shared entity contributions is still unestablished; it is a graph-specific audit/test requirement, not a proven missing delete API.[^weknora]
- Existing parsing, adaptive/parent-child chunking, weighted RRF, shared reranking/MMR, guarded agents and revisioned wiki should be the baseline. RAGFlow being Go at this pin does not make its DI, storage schemas, query DSL or native dependencies drop-in compatible.[^weknora][^ragflow]

## Product priorities and acceptance gates

All priorities and gates below are **Synthesis / proposals**, not observed product results.

| Order | Work | Design reference | Acceptance gate |
| --- | --- | --- | --- |
| P0 | Freeze upstream pin, reproducible deployment, key/registration/RBAC/egress posture, redacted retrieval trace and regression harness | WeKnora's existing controls; Ragas metric contracts | Baseline artifacts retained; cross-tenant and unauthorized-tool tests pass; restore/rollback exercised |
| P1 | Structure-aware table splitting, exact token budgets and stable source locators | RAGFlow chunker families; WeKnora protected spans and offsets | Large tables retain repeated headers and source mapping; tokenizer-limit and citation regression cases pass |
| P1 | Domain synonym/phrase expansion and title/question/keyword field weighting, then optional local scoring fallback | RAGFlow QueryBuilder and reranker | Held-out recall/ranking improves without violating latency/cost budget; Vietnamese/English terminology evaluated separately |
| P1 enterprise | Durable failed-item/deletion replay; connector lease/idempotence tests; source ACL enforcement if required | RAGFlow sync checkpoints/leases; OpenRAG ACL pipeline | Crash/retry does not lose failed items; revoked documents cannot reach any answer or derived surface |
| P2 | Embedding-space identity and versioned re-embedding migration | LightRAG compatibility markers; OpenRAG multi-space search | Wrong-space vectors refused; new index validated before switch; rollback and keyword fallback tested |
| P2 document-heavy | Table/image/equation sidecar enrichment and replayable parser options | LightRAG multimodal pipeline | Measured multimodal gain, locator fidelity, bounded VLM cost and safe file containment |
| P3 | Relation-vector/global retrieval and contribution-owned graph recovery | LightRAG retrieval and deletion | Multi-hop gain exceeds extraction/query cost; deleting one source preserves other sources' evidence |
| Experiment only | Alternative fusion or semantic splitting | txtai fusion; LightRAG chunking | One-variable ablation beats current baseline; otherwise leave disabled |

The references establish mechanisms, not guaranteed benefits: RAGFlow documents format-aware chunking, field-aware ranking and checkpoint/lease behavior; OpenRAG propagates ACLs and routes model-qualified vectors; LightRAG documents parser directives, token-budgeted graph retrieval, vector markers/rebuild and contribution-aware deletion; txtai offers fusion alternatives.[^ragflow][^openrag-repo][^lightrag-aaebfe1][^txtai-repo]

## Implementation shape: one owner for lifecycle and authorization

**Proposed topology:** keep UI/API, identity, KB/document metadata, job orchestration and canonical citations in WeKnora. Extend the existing chunker/search/rerank services through small interfaces. Keep heavyweight Python/native model execution behind the existing parsing boundary or an isolated worker when necessary; do not make Go → full LightRAG server → independent stores a default query dependency.[^weknora]

**Proposed contracts:**

- A parsed block records document version, block type, page/span/bounding-box locator when available, content and content hash. Chunk lineage records parser/chunker/options versions; chunk identity should distinguish source versions and content rather than rely on order alone. These are proposed contracts, not claims about current schemas.
- A retrieval hit retains document/chunk revision, source locator, authorization scope, retrieval branch, raw/fused/rerank scores and the reason for degradation. Do not compare raw scores across different embedding spaces; embed/query each compatible space and use rank-based fusion only after authorization.
- Final context budgeting counts system instructions, history, query, tool/graph content, source wrappers and output reserve. Only sources actually supplied to the model may become current citation evidence. Preserve WeKnora's original-chunk semantics while borrowing LightRAG's budget ordering.[^weknora][^lightrag-aaebfe1]
- For sync, choose either checkpoint-after-durable-success or checkpoint-after-durable-retry-record. Cursor advancement must not make failed-item recovery depend on a human remembering to run a full refresh. RAGFlow is a contract reference, not a proposal to import NATS/Kvrocks into WeKnora.[^weknora][^ragflow]

## Authorization must cover derived knowledge

**Synthesis / design requirement:** if source-level ACLs are needed, propagate owner/principal/group and ACL-version metadata through ingestion and enforce access during retrieval and authoritative source resolution, before rerank, model context or streaming. The design is informed by OpenRAG's ACL-to-chunk/DLS boundary, not a claim that its implementation solves every downstream case.[^openrag-repo]

For WeKnora, test chunk search, document/image endpoints, agent tools, MCP, caches, conversation replay, auto-wiki and graph-derived evidence. A wiki page or merged graph entity built from several documents must not become a permission bypass: either partition compilation by a permission-compatible audience, preserve/enforce contribution provenance, or disable that derived surface for mixed-ACL corpora until safe behavior is defined. Existing wiki revisioning and live-chunk graph checks are useful mechanisms, not proof of source-ACL noninterference.[^weknora]

A caller-facing filter is not authorization. Recheck revocation before serving sensitive cached/derived results and define what happens to old conversations after permissions change. Prompt fencing is defense in depth; tools still need capability checks in code.[^weknora][^openrag-repo]

## Evaluation and delivery sequence

**Proposal:** build a reviewed development/held-out set from real documents: ordinary lookup, scanned/layout-heavy PDFs, large tables, Vietnamese/English acronyms, multi-document questions, no-evidence questions, and adversarial permission/injection/deletion cases. Retain exact model-visible context, pipeline configuration and degraded-path traces without logging secrets or unauthorized text.

Measure retrieval recall/rank, answer/reference correctness, support by actual context, citation identity/support, abstention, p50/p95 latency, model cost, ingestion failure and recovery. Pin Ragas metric API, judge, prompts and invalid-score policy; its faithfulness metric checks consistency with context, not world truth. Security and recovery invariants are release gates even when they do not improve answer accuracy.[^ragas-298b682]

Suggested releases, without unsupported calendar estimates:

1. **Safe baseline:** deployment/hardening + trace/eval + existing citation tests.
2. **Document-quality release:** table-aware splitting + tokenizer budgets + controlled lexical/field boosts; local fallback only if measured useful.
3. **Enterprise release:** durable failed-item replay + required connectors + source ACLs and permission-safe derived surfaces.
4. **Advanced release:** vector migration + selective multimodal enrichment, then graph retrieval if multi-hop evaluation justifies it.

Keep one feature flag and one reviewable change series per mechanism; avoid unnecessary upstream file moves, keep extension wiring small, preserve PostgreSQL/SQLite migration parity when supporting both, and continuously merge upstream fixes. Sidecar RPCs must carry authorization context and cannot create a second untracked document lifecycle. Audit applicable file/component licenses before reuse; rewriting is not a substitute for a license review.[^weknora]

## Relationships

- **Uses:** [platform comparison](rag-platform-comparison.md) for positioning, but corrects its earlier uncompiled WeKnora citation row.
- **Depends on:** [WeKnora citation/source boundary](weknora-citations-source-boundary.md), [sync contracts](weknora-datasource-sync.md), [security](weknora-security.md), and [source coverage](weknora-source-map.md).
- **Uses:** [grounded-accuracy evaluation](grounded-accuracy-evaluation.md) as additional evaluation design guidance; its vendor-reported numbers are not fork performance targets.

## Evidence and coverage limits

Inputs are the compiled feature pages below plus targeted raw inspection of WeKnora at `fd7a2586fd58`. Other platforms' raw implementations were not re-researched for this roadmap. All platform concepts remain draft static evidence; no upstream tests/builds/deployments, retrieval benchmarks, cloud connectors, graph deletes, model calls or license-compliance audit ran. Raw snapshots were not edited. The older requested output was reviewed as a proposal, not adopted as independent evidence. Scope assumes a team/private document knowledge product; ACL, multimodal and graph priorities depend on actual product requirements.

[^weknora]: Revision `fd7a2586fd58`, canonical [README](../raw/WeKnora/README.md); compiled [architecture](weknora-backend-architecture.md), [ingestion](weknora-document-ingestion.md), [retrieval](weknora-hybrid-retrieval.md), [citations](weknora-citations-source-boundary.md), [sync](weknora-datasource-sync.md), [graph](weknora-graph-multimodal-retrieval.md), [wiki](weknora-wiki-compilation.md), [configuration](weknora-configuration.md), [security](weknora-security.md), [source map/license limits](weknora-source-map.md). Follow-up raw locators: `chat_pipeline/citation_sources.go::attachCitationSources, expandCitationSources`; `chat_pipeline/references.go::prepareMessagesWithModelContext`; `chat_pipeline/query_expansion.go::expandQueries`; `internal/modelcontext/citations.go::ExpandText, citationTag`; `internal/application/service/datasource_service.go::streamSyncHandler.Emit, Checkpoint, applyFetchedItem, processSyncStreaming`; `knowledge_delete.go::executeKnowledgeDelete` (graph cleanup). Chat-pipeline paths are under `internal/application/service/`.
[^ragflow]: Revision `1731e54b3aa0`, canonical [README](../raw/ragflow/README.md); via [ingestion](ragflow-ingestion.md), `internal/ingestion/component/chunker/general.go::generalStrategyForFileType`; [retrieval](ragflow-retrieval.md), `internal/service/nlp/query_builder.go::Question`, `reranker.go::RerankWithKNN, HybridSimilarity`; [sync](ragflow-connectors.md), `internal/syncer/sync_runner.go::Run, processDocument`, `connector_lock.go::TryLock`, `connector/ssrf.go::connectorRequest`. Native-build and architecture limits are recorded in the platform comparison.
[^openrag-repo]: Revision `6fc819d3ec10`, canonical [README](../raw/openrag/README.md); via [connectors/ACL](openrag-connectors.md), `src/connectors/base.py::DocumentACL`, `securityconfig/roles.yml`; [hybrid retrieval](openrag-hybrid-retrieval.md), `src/services/search_service.py::_search`, embedding-space discovery, `custom_components/openrag/opensearch_multimodal.py::fence_untrusted_text`. ACL refresh, full synchronization and model-space behavior were not runtime-verified.
[^lightrag-aaebfe1]: Revision `aaebfe1bb8d5`, canonical [README](../raw/LightRAG/README.md); via [multimodal parsing](lightrag-parsing-multimodal.md), `pipeline.py::analyze_multimodal`, `parser/routing.py::resolve_parser_directives`; [retrieval](lightrag-retrieval.md), `operate.py::_build_context_str`, `utils.py::process_chunks_unified`; [embedding recovery](lightrag-embedding-recovery.md), `kg/vector_space.py::assert_vector_space_matches`, `tools/rebuild_vdb.py`; [deletion](lightrag-deletion.md), `lightrag.py::_purge_kg_contributions`. Paths relative to `lightrag/`, except `tools/`.
[^txtai-repo]: Revision `738aac498ccb`, canonical [README](../raw/txtai/README.md); via [retrieval](txtai-retrieval.md), `src/python/txtai/embeddings/search/hybrid.py::Hybrid, LogOdds` and `pipeline/text/reranker.py::Reranker`; alternative fusion quality remains unmeasured.
[^ragas-298b682]: Revision `298b68274234`, canonical [README](../raw/ragas/README.md); via [RAG metrics](ragas-rag-metrics.md), “Collections implementations inspected” and “Migration and experiment interpretation”; `src/ragas/metrics/collections/faithfulness/metric.py::Faithfulness.ascore`, context precision/recall collection metrics and their invalid-score limits. This roadmap specifies no executed evaluation.
