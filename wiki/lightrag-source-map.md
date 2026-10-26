---
type: SourceMap
title: LightRAG source map and coverage
description: Pinned source identity, per-artifact inspection ledger, redacted disclosure handling, exclusions, and remaining execution and coverage limits.
tags: [rag, operations, source-map, provenance]
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

**Observed:** this compilation treats `raw/LightRAG/` as one read-only composite code source at revision `aaebfe1bb8d55deb6a4304d357a3bf4c92fcd40a`. Five Explore subagents reviewed core/pipeline, retrieval/models, storage/concurrency, API/UI/auth, and operations/testing; the curator inspected parser contracts, selected multimodal logic, the full entry README and its architecture diagram. **Limit:** targeted static inspection does not mean complete files or passing runtime tests; all compiled concepts remain draft for material coverage and verification gaps.[^lightrag-aaebfe1]

## Identity and trust

| Field | Inspected value |
| --- | --- |
| Entry point / scope | `raw/LightRAG/README.md` / `raw/LightRAG/` |
| Revision / commit date | `aaebfe1bb8d55deb6a4304d357a3bf4c92fcd40a` / 2026-10-14 |
| Commit subject | Merge pull request #4210 from ModestXin/fix/pgvector-filtered-ann |
| Upstream | Git remote `git@github.com:HKUDS/LightRAG.git` |
| Distribution / runtime | `lightrag-hku` 1.5.8, API 0347; Python ≥3.10 |
| License | MIT; copyright 2025 LightRAG Team |
| Languages | Python backend; TypeScript/TSX frontend; shell/YAML/config; multilingual docs |
| Tracked artifacts | 1,331 |

The source describes capabilities and benchmark results as its authors' claims; package manifests establish intended dependencies, not successful resolution. The paper linked by README citation (`2410.05779`) and external datasets/model weights were not independently retrieved.[^lightrag-aaebfe1]

## Durable compilation destinations

[LightRAG overview](lightrag.md) navigates seventeen supporting concepts including this map: architecture, ingestion, chunking, parsing/multimodal analysis, extraction/merge, deletion, retrieval, query contracts, model roles, storage, concurrency, embedding recovery, API/UI, security, deployment and testing. The existing [RAG-Anything architecture](rag-anything-architecture.md) gains comparison links without a supersession or compatibility assertion. A separate semantic reviewer checked all eighteen compiled pages and selected source regions; corrections clarified default-off image analysis, role-partitioned multimodal caches, fresh references paired with cached answer text, rerank defaults/fallbacks, configuration layering and the flush-list boundary.

## Complete tracked-artifact ledger

[Per-artifact TSV ledger](lightrag-source-coverage.tsv) accounts for every tracked path with disposition, reviewing pass, separate syntax result and explicit limit. Paths in it are relative to the source scope. “Pending” Python can have passed syntax parsing while still lacking substantive inspection; symbol-level grep is not full-file reading.

| Disposition | Artifacts | Meaning |
| --- | ---: | --- |
| Targeted static | 230 | Selected symbols, configuration, assertions or document regions read; remainder not implied audited |
| Visual inspection | 1 | README architecture diagram: graph indexing, low/high keyword retrieval, original text evidence; not quantitative validation |
| Sensitive/redacted | 1 | Compose environment sample; credential/key presence only compiled, values withheld |
| Excluded | 26 | Translated duplicate docs, housekeeping/agent metadata, branding/promotion, and historical UI screenshot not used for current behavior |
| Pending | 1,073 | Inventoried but substantive content not inspected; syntax-only where marked |
| **Total** | **1,331** | All tracked artifacts accounted for |

**Observed coverage limits:** large modules (`lightrag.py`, `pipeline.py`, `operate.py`, `utils.py`, storage adapters and setup script) were read in targeted regions. The ledger does not certify every branch in a targeted file. Selected tests were inspected as written intent, none executed. Chunker registry/plugins, smart-heading feature/guardrail/flow modules and file-fingerprint contracts include symbol/contract-level inspection. Backend coverage emphasizes naming, isolation, capability and migration regions rather than exhaustive SQL/query/cursor behavior.[^lightrag-aaebfe1]

## Sensitive input handling

A prefix-pattern screen initially found no high-specificity matches. The operations review subsequently identified non-placeholder-shaped provider/service keys in `env.docker-compose-full` and an unclear disclosure boundary; values and endpoint details were not copied. Compilation paused, unfinished wiki drafts were removed, and the human approved resuming redacted findings. **Unverified:** live validity, rotation, endpoint ownership, and deployment authorization. Shared sample passwords and secret-shaped fixtures were not promoted to usable credentials. Raw evidence remains unchanged; see [security boundaries](lightrag-security.md).[^lightrag-aaebfe1]

## Executed versus unexecuted checks

**Reproduced, syntax only:** all 818 tracked Python files passed `ast.parse` under Python 3.12.3/Linux with no repository imports. Record: a per-file JSON was written to `outputs/lightrag-ingest/static-checks.json` during the ingest, but that disposable artifact was not retained in this repository, so the per-file result is not re-auditable here. This is not pytest, dependency resolution, a provider call or an API smoke test.

Inspection fingerprint: `eb40b5cf2d89925a2a15e8a7ea20f613abea900655fd9541bb21a23f74de2cf3` (SHA-256 of sorted relative path bytes + NUL + raw SHA-256 digest bytes for each tracked file). This is an ingest fingerprint, not an upstream signature or attestation. Initial, pre-resumption and final source Git checks were clean; a recomputed tracked-content fingerprint matched the initial value.

No upstream code, tests, model, external parser, HTTP service, frontend build, image/container, Helm rendering, database/migration or destructive repair was executed. Configured CI intent and reported research measurements are separate from these checks. Wiki structural/citation/path validation concerns the compiled artifact, not platform behavior.

## Pending material closure and follow-up

- Most test bodies/fixtures, golden DOCX/sidecar examples, frontend graph/admin internals, and sample programs.
- Native DOCX/Markdown converter internals and the sidecar IR/writer; external MinerU/Docling request/archive handling, service configuration and upstream dependencies.
- Recursive splitter body, full custom chunker/plugin lifecycle, comprehensive table/span accuracy, smart-heading algorithm and NLP-model behavior.
- Ingress/scan mailbox bodies, all atomic-file helper behavior, custom-chunk journaling, reservation interleavings and dedicated purge/concurrency design contracts not otherwise recorded as inspected.
- Most provider modules, full vector-space adoption behavior, backend pagination/CAS/transactions and backend integration matrices. Some source design docs are forward-looking; adoption gates are not assumed implemented.
- `uv.lock` dependency contents, external images/digests, registry signatures, schema/AGE compatibility, downloaded NLP/tokenizer/model assets and third-party licenses beyond the repository's own MIT statement.
- External paper, linked flowchart images, benchmark datasets, provider APIs, parser services and optional toolchains: not fetched. Remote architecture flowcharts are excluded as redundant with inspected in-tree code/diagram for the claims retained, not certified equivalent in every detail.

**Idempotency:** match this normalized scope plus revision and reconcile the ledger before re-ingest. The 18-page compilation is not complete coverage; a follow-up should inspect named pending regions and mutate only newly established, changed or connected knowledge—not append a second source identity for a supporting module.

[^lightrag-aaebfe1]: Revision `aaebfe1bb8d55deb6a4304d357a3bf4c92fcd40a`: `README.md` complete entry-point inspection and local links; `README.assets/b2aaf634151b4706892693ffb43d9093.png` full architecture diagram; `LICENSE`; `pyproject.toml`; `lightrag/_version.py`; `lightrag/{lightrag,pipeline,operate,base,utils,llm_roles,storage_migrations}.py` selected regions; parser/registry/routing/base and multimodal contracts; selected storage/provider/API/frontend/deployment/evaluation/test artifacts individually enumerated in the [coverage ledger](lightrag-source-coverage.tsv); `env.docker-compose-full` redacted key-presence inspection. Git identity/inventory and AST/fingerprint checks were performed by the curator; human approval and workflow facts describe this compilation session, not upstream runtime behavior.
