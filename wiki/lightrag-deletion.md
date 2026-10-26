---
type: Concept
title: LightRAG deletion and recovery boundaries
description: Reservation-owned document purge, recovery proofs, contribution ownership, cache-based graph rebuilding, and guarded admin graph writes.
tags: [rag, operations, recovery, deletion]
status: draft
created: 2026-10-26
generated: { by: llm-wiki-agent/1, at: 2026-10-26T09:15:00Z }
stale_after: 2027-01-24
sources:
  - id: lightrag-aaebfe1
    resource: ../raw/LightRAG/README.md
    scope: ../raw/LightRAG/
    kind: code
    revision: aaebfe1bb8d55deb6a4304d357a3bf4c92fcd40a
    title: LightRAG repository
---

**Observed:** document deletion is a reservation-owned recovery workflow: it proves discoverable graph contributions, verifies candidate ownership, deletes or rebuilds affected records, and only then removes document/chunk metadata. **Synthesis:** deletion is not a blind filter-by-document-ID operation, and missing recovery evidence can intentionally prevent it.[^lightrag-aaebfe1]

## Purge and ordering

- `adelete_by_doc_id` takes the pipeline busy slot or joins an authorized batch-delete job; conflicting ownership can return forbidden, while recovery-required state blocks normal work.
- `_purge_kg_contributions` builds a recovery superset from anchors/tracking and verifies each candidate's ownership against tracking plus graph source IDs. Records are classified for outright removal or rebuilding from surviving evidence.
- `rebuild_knowledge_from_chunks` uses cached extraction results rather than new LLM extraction calls, with best-effort/rollback handling. A missing or unusable cache is therefore a recovery limit, not an invitation to invent evidence.
- Derived contributions are repaired and flushed before chunks are deleted; anchors are removed last. Purge progress is journaled in `doc_status.metadata.kg_purge`.
- A no-chunk-ID branch fails closed rather than blindly deleting unrelated rows. Final document cleanup deletes status before full-document data so retries can recognize an already-deleted document.[^lightrag-aaebfe1]

**Observed:** optional `delete_llm_cache=True` pools chunk, journal, prior deletion, and smart-heading cache IDs and checks for surviving keys. The default is false. **Synthesis:** retention and cost-saving caches are operationally connected to recovery; “delete a document” and “erase every associated cache value” are separate requested behaviors.[^lightrag-aaebfe1]

## Admin graph changes

**Observed:** entity/relation delete/edit/create and entity-merge APIs check recovery-required state. The admin write gate is conditional on the graph backend's single-writer capability, notably NetworkX. Entity merge supports concatenate/keep-first/keep-last/join-unique policies and adjusts redirected relation weights. These endpoints do not independently establish per-user authorization; see the shared API security boundary.[^lightrag-aaebfe1]

**Observed:** `_insert_done` flushes the twelve stores returned by `_index_storages()` through `_flush_storages`, which accepts a store list and raises `IndexFlushError` on exceptions or explicitly declined commits. **Synthesis:** a successful Python method return from an earlier mutation stage is not proof that every derived store durably committed.[^lightrag-aaebfe1]

## Relationships

- **Depends on:** [Extraction anchors and cache reachability](lightrag-extraction.md).
- **Depends on:** [Strict storage reads](lightrag-storage.md) and [concurrency/flush contracts](lightrag-concurrency.md).
- **Related:** [Vector-only recovery](lightrag-embedding-recovery.md) rebuilds vector indexes without removing authoritative graph/chunk evidence.
- **Exposed by:** [API/UI](lightrag-api-ui.md); [security](lightrag-security.md) limits which callers can reach the shared write surface.

## Evidence limits

Observed source control flow, not executed purge/rollback/restart evidence. Dedicated purge design contracts, all failure journals, backend strict-read completeness, concurrent deletes and destructive force-reset semantics remain only partially inspected. No deletion or repair command ran; see [coverage](lightrag-source-map.md).

[^lightrag-aaebfe1]: Revision `aaebfe1bb8d55deb6a4304d357a3bf4c92fcd40a`: `lightrag/lightrag.py::LightRAG.adelete_by_doc_id, _purge_kg_contributions, _admin_write_gate, _raise_if_recovery_required, amerge_entities, _index_storages, _flush_storages` (purge 6015–6105; deletion 6727–7375; admin 7475–7513, 7925–7955, 8123–8360); `operate.py::rebuild_knowledge_from_chunks` (1102–1145); `base.py::BaseGraphStorage.requires_single_writer`; `api/routers/document_routes.py` deletion and recovery route registration; `api/routers/graph_routes.py` admin route registration.
