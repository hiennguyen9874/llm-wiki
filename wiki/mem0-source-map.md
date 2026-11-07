---
type: SourceMap
title: Mem0 source map and documentation discrepancies
description: Coverage ledger, inspection limits, and consequential documentation conflicts for the Mem0 repository snapshot.
tags: [agent-memory, mem0, source-map]
status: draft
created: 2026-11-06
generated: { by: llm-wiki-agent/1, at: 2026-11-06T17:08:00Z }
stale_after: 2027-02-06
sources:
  - id: mem0
    resource: ../raw/mem0/README.md
    scope: ../raw/mem0/
    kind: code
    revision: d16b8df
    title: Mem0 repository
---

This map records selective static inspection of the Mem0 repository; it is not a claim of exhaustive package coverage. The entry point is `README.md`, scope is `raw/mem0/`, and the fixed revision is recorded in metadata. Four parallel reviews covered core memory, server/security, clients/integrations, and providers/evaluation; selected implementation paths were rechecked by the curator.[^mem0]

## Coverage ledger

- **Inspected selectively:** Python `mem0/memory/`, `mem0/configs/`, `mem0/utils/`, `mem0/vector_stores/`, hosted `mem0/client/`; `server/` app, auth, routers, deployment and selected dashboard auth; `mem0-ts/`, `cli/`, selected `integrations/` and `skills/`; selected docs, tests, CI and `pyproject.toml`.[^mem0]
- **Unavailable:** `evaluation/` is an uninitialized submodule; benchmark harness and data were not inspected. External hosted-service implementation, external model assets and linked websites were not inspected.[^mem0]
- **Excluded or pending:** generated lockfile and generated plugin copies are not treated as primary evidence; decorative README images and duplicated examples are excluded. Other provider adapters, integration internals, dashboard features, remaining examples and docs remain pending, not comprehensively audited. No source code, tests, builds, services or benchmarks were executed.[^mem0]

## Contradictions

- The README describes three retrieval signals scored in parallel; the Python search implementation invokes the stages sequentially, with parallelism inside entity lookups. This is a code-versus-prose distinction, not a runtime measurement.[^mem0]
- Some older repository guidance and `LLM.md` describe OSS graph-store configuration, whereas the current migration guide says it was removed and the inspected `MemoryConfig` has no graph-store field.[^mem0]
- The README and migration guide disagree on reported benchmark values; see [benchmarks](mem0-benchmarks.md).[^mem0]

All linked concepts are draft because source closure is incomplete and behavior is statically inspected rather than reproduced. A complete re-ingest must reconcile pending paths rather than assuming full coverage.

[^mem0]: Revision `d16b8df6`; `README.md::New Memory Algorithm (April 2026)`; `mem0/memory/main.py::Memory._search_vector_store`, `Memory._compute_entity_boosts`; `mem0/configs/base.py::MemoryConfig`; `LLM.md::Graph Memory`; `docs/migration/oss-v2-to-v3.mdx::Overview`; `.gitmodules::submodule evaluation`.
