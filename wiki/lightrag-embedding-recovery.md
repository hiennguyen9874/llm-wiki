---
type: Concept
title: LightRAG embedding-space compatibility and recovery
description: Model-space markers, typed compatibility refusals, legacy-data limits, and the destructive vector-only rebuild workflow.
tags: [operations, rag, embeddings, recovery]
status: draft
created: 2026-10-26
generated: { by: llm-wiki-agent/1, at: 2026-10-26T08:47:00Z }
stale_after: 2027-01-24
sources:
  - id: lightrag-aaebfe1
    resource: ../raw/LightRAG/README.md
    scope: ../raw/LightRAG/
    kind: code
    revision: aaebfe1bb8d55deb6a4304d357a3bf4c92fcd40a
    title: LightRAG repository
---

**Observed:** LightRAG tracks embedding compatibility through model/dimension container names or out-of-band vector-space markers and exposes `lightrag-rebuild-vdb` to regenerate vectors from graph and chunk stores. **Synthesis:** changing the embedding function is a data migration, not a harmless query-time model swap; compatibility checks also have explicit legacy-data blind spots.[^lightrag-aaebfe1]

## Provenance and refusal

- **Observed:** Milvus, Qdrant and PostgreSQL vector container names use a folded model/dimension suffix. Nano, FAISS, Mongo and OpenSearch use non-searchable marker locations such as metadata or sidecars; provenance must not be fabricated as a retrievable vector record.
- `assert_vector_space_matches` raises typed `VectorSpaceMismatchError` for established incompatible metadata. Missing model/dimension evidence does not itself refuse legacy containers. A caller without a declared model cannot certify a marker just because the dimension matches.
- **Reported design contract:** non-empty unmarked data must not be marked as belonging to the current model without an adoption probe. **Observed review limit:** the reviewer did not locate the documented adoption/empty-container gate in `LightRAG.initialize_storages` at this revision, and FAISS comments still describe the probe prospectively. Treat automatic legacy certification as unestablished; same-dimension swaps in unmarked legacy data may escape detection.[^lightrag-aaebfe1]

## Rebuild workflow: observed tooling, not an executed procedure

1. **Stop the server and every other writer.** The tool rewrites vector stores; concurrent writers can corrupt data or lose updates on any backend.
2. Configure the intended embedding model/dimension through the same environment/factory path the server uses.
3. Invoke `lightrag-rebuild-vdb`; its interactive workflow offers rebuilding all vector stores. Entity vectors come from graph nodes, relationship vectors from graph edges, and chunk vectors from `text_chunks`.
4. Wait for successful completion before restarting. **Reported:** there is no persisted readiness marker preventing premature service restart.

**Observed:** the recovery tool tolerates the specific typed model-space refusal while initializing for replacement; unrelated cluster, credential, and corrupt-file errors are not a general license to drop data. **Reported:** the graph and chunk KV sources are not the rebuild targets. Do not delete the working directory or manually drop containers as a prerequisite. The check option only detects selected graph-to-vector misses, does not establish model equivalence, and initialization may still run DDL or legacy migrations.[^lightrag-aaebfe1]

## Documentation discrepancy

**Reported:** README “Embedding Models” says no re-embedding tool exists and suggests deleting vector-related tables when changing models. **Observed:** README SDK Note 1, its maintenance-tool catalog, `ProgramingWithCore`, the executable rebuild tool, and its dedicated README describe the opposite recovery path. **Synthesis:** the no-tool statement is stale at this pin; retain the discrepancy for upstream correction, but use the implemented vector-only rebuild workflow rather than deleting authoritative graph/chunk data. PostgreSQL's model-suffixed tables can leave old model tables behind; rebuilding the current space is not proof those old containers were removed.[^lightrag-aaebfe1]

## Relationships

- **Depends on:** [Storage backends](lightrag-storage.md) for model-specific naming and metadata.
- **Depends on:** [Concurrency contracts](lightrag-concurrency.md) for writer isolation; the rebuild warning exceeds ordinary API locking.
- **Used by:** [Model integrations](lightrag-models.md) when embedding configuration changes.

## Evidence limits

Static inspection of contracts, selected backend regions, and tool control flow; no vector rebuild, database migration, adoption probe, or model swap was executed. Full backend marker persistence and index-readiness recovery remain pending in the [source map](lightrag-source-map.md).

[^lightrag-aaebfe1]: Revision `aaebfe1bb8d55deb6a4304d357a3bf4c92fcd40a`: `lightrag/base.py::BaseVectorStorage._generate_collection_suffix`; `kg/vector_space.py::assert_vector_space_matches`; `exceptions.py::VectorSpaceMismatchError`; `kg/{nano_vector_db_impl,faiss_impl,mongo_impl,opensearch_impl,milvus_impl,qdrant_impl,postgres_impl}.py` model-space initialization, particularly `faiss_impl.py` 1458–1484 and `postgres_impl.py` 4022–4042; `lightrag.py::LightRAG.initialize_storages` targeted symbol search; `tools/rebuild_vdb.py` initialization and confirmation paths; `tools/README_REBUILD_VDB.md` 5–11, 45–64, 70–121, 135–141; `docs/design/VectorSpaceProvenance.md` marker/adoption contract and 442–445; README “Embedding Models”, SDK Note 1 and maintenance tools; `docs/ProgramingWithCore.md` “Switching embedding models”.
