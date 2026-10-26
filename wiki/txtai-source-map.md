---
type: SourceMap
title: txtai source map and coverage
description: Pinned source identity, tracked-artifact coverage ledger, exclusions, reconciliation decisions, and remaining evidence limits.
tags: [rag, txtai, source-map, provenance]
status: draft
created: 2026-10-26
generated: { by: llm-wiki-agent/1, at: 2026-10-26T09:14:52Z }
stale_after: 2027-01-24
sources:
  - id: txtai-repo
    resource: ../raw/txtai/README.md
    scope: ../raw/txtai/
    kind: code
    revision: 738aac4
    title: txtai repository
---

**Observed:** this compilation covers the local NeuML txtai repository at commit `738aac4`, using four parallel Explore subagents plus curator inspection and reconciliation. The [658-artifact ledger](txtai-source-coverage.tsv) is the package coverage/accounting surface: it separates targeted static inspection, declarations/credential-only screening, syntax-only coverage, pending material, and exclusions. **Limit:** neither this map nor the concept pages claim complete behavioral coverage or a successfully running txtai installation.[^txtai-repo]

## Source identity

| Field | Inspected value |
| --- | --- |
| Canonical entry point / scope | `raw/txtai/README.md` / `raw/txtai/` |
| Revision / author timestamp | `738aac4` / `2026-10-22T19:56:53+01:00` |
| Commit subject | Encode images without a format as PNG in ImageEncoder (#1467) |
| Upstream | `https://github.com/neuml/txtai`; Git remote uses the same repository over SSH |
| Package / runtime | `txtai` 9.15.0; Python ≥3.11; optional `txtai_minimal` distribution mode |
| Attribution / license | David Mezzetti / NeuML in `CITATION.cff`; Apache-2.0 (license header inspected) |
| Source languages | Python implementation, YAML/configuration, English documentation and notebook examples |
| Snapshot | 658 tracked artifacts; source worktree clean at initial inspection |

Citation metadata's `date-released: 2020-08-11` is not the date of this snapshot. Source-author explanations and README capability statements remain Reported unless directly grounded in the inspected implementation.[^txtai-repo]

The tracked-file inspection fingerprint is `0f075faccb64c58b1280749bb90f2cd3e1e8e74f0c74ae2245ab55bbf73076ae` (SHA-256 over sorted relative UTF-8 path bytes, NUL, then the file's raw SHA-256 digest bytes). It is a session fingerprint, not an upstream signature or attested build.

## Retrieval map

Start with [txtai overview](txtai.md) and [architecture/stack](txtai-architecture.md), then:

- [Retrieval/ranking](txtai-retrieval.md): query dispatch, fusion, ANN/sparse constraints, image-model path.
- [Persistence](txtai-persistence.md): SQL content, initialization versus load, IDs, mutations, archives/cloud.
- [Graph/topics](txtai-graph.md): inferred/manual edges, communities, graph queries, backend lifecycle.
- [Extraction/multimodal pipelines](txtai-pipelines.md): backend selection, segmentation, tables/images/audio.
- [LLM/RAG](txtai-rag.md): generation adapters, context, outputs, reference semantics.
- [Agents/workflows](txtai-agents-workflows.md): tools, skills, memory, tasks, schedules, isolation limits.
- [API/cluster/MCP](txtai-api.md): startup, route selection, compatibility dispatch, unresolved transport behavior.
- [Security](txtai-security.md): trusted configuration, file/network and artifact boundaries.
- [Operations/testing](txtai-operations.md): packaging, deployment, configured CI and unexecuted checks.

## Coverage ledger interpretation

Every tracked source path has exactly one ledger row; code imports, package entry points, supporting configuration, documentation, tests, examples, and assets remain attributable to this one source identity. No supporting module is treated as a separate source. `inspected-targeted` means substantive code/document/diagram regions were examined, **not** full-file or transitive-dependency audit. `declarations-content-pending` and `screened-content-pending` do not establish implementation behavior. All Python paths additionally have an AST result, independently of content coverage.

Coverage totals: **302 targeted inspections**, **174 syntax-only/content-pending**, **123 inventory-only pending**, **45 exclusions**, **9 credential/context-screened with content pending**, and **5 declaration-only with content pending** (658 total). These are accounting categories, not measures of tested functionality.

The ledger's reviewer labels identify architecture/operations, retrieval/persistence/graph, feature pipelines/agents, API/security, and curator passes. Overlapping inspections count once. Read-only subagent findings delivered in conversation were normalized into session path lists before merging; declarations and notebook screening were downgraded where appropriate.

### Material coverage and limits

| Artifact family | Disposition and destination |
| --- | --- |
| Entry point, citation, packaging, CI, Docker | Targeted inspection; license header only; operations/architecture/source identity |
| Embeddings/index/search, dense+sparse ANN/scoring | Broad targeted inspection; GGML tensor internals and unreviewed helper/backend regions remain pending; retrieval/persistence |
| Content SQL/schema/encoders, serializers, archives/cloud | Targeted inspection; no database/cloud/native-format round-trip; persistence/security |
| Graph implementations/queries/topics | Targeted inspection and sampled assertions; no factual/quality/scale verification; graph |
| Data, LLM, image and selected audio pipelines | Targeted mechanism inspection; HTML converter tail, complete audio toolkit, training and other text pipelines remain incomplete; pipelines/RAG |
| Agents/tools/workflows | Main composition/tools plus selected tasks inspected; external smolagents/MCP runtime not vendored/audited; agents/API/security |
| API routers, auth, OpenAI selection, MCP mount, cluster | Static inspection; no transport/auth/lifecycle execution; API/security |
| Tests | Selected assertions or test declaration indexes only; all unexecuted; remaining tests syntax-only |
| Notebooks/examples | Selected image and RAG examples inspected; several extension/credential contexts screened only; most notebooks pending |
| Diagrams | Primary architecture, RAG, formats, agent/LLM/task/workflow/schedule, indexing/query/API/cloud and embeddings/search/pipeline diagrams visually inspected; small/low-contrast labels not used as sole implementation evidence |
| Alternate art/branding | Editable Excalidraw and dark-theme variants excluded as artwork/alternate presentation; branding/demo media excluded, not used as architecture or benchmarks |
| Other local docs/config/assets | Pending unless their explicit ledger row says inspected/excluded; no blanket documentation parity claim |

External model weights, remote technical paper/articles, JavaScript/Java/Rust/Go bindings, upstream framework internals, MLflow plugin and remote screenshots, native libraries, cloud/shard/parser services, and release fixture archive were not downloaded or audited. Importable package references remain outside this snapshot's evidentiary closure; they are neither silently counted as inspected nor replaced by assumed behavior.[^txtai-repo]

## Reconciliation decisions

- **Observed/Synthesis:** generic object forwarding plus STVectors/CLIP examples supports image embeddings. A grep-only “no pixel vectors” inference was rejected.
- **Observed:** SQL client fresh initialization clears content tables; ordinary `load` starts a session without that call. Relational graph `create` versus `load` has a similar consequential distinction.
- **Observed:** built-in authorization hashes raw credentials; stored digest is not itself accepted as the bearer token.
- **Limit:** cluster sets no explicit timeout override; external library defaults prevent concluding “infinite timeout.” MCP header propagation likewise remains unknown, not a demonstrated bypass.
- **Observed:** empty RAG context leaves reference `None`; post-hoc similarity reference is not evidence-span grounding. Workflow fixed ordering is not a claim that arbitrary actions are deterministic.
- **Observed:** coverage-threshold enforcement is Ubuntu-only in the inspected CI matrix. Sparse shortcut model documentation and scheduler Dockerfile documentation differ from implementation.[^txtai-repo]

These reconciliations preserve narrower implementation claims rather than storing incompatible agent interpretations as unresolved platform facts.

## Session checks and trust

**Reproduced, compilation-session syntax check only:** all **409** tracked Python files passed standard-library `ast.parse` on Python **3.12.3/Linux**. No upstream imports, application tests, services, models, builds, migrations, workflows, provider calls, benchmarks, or exploit attempts ran. Syntax parsing establishes none of those outcomes.

Heuristic private-key/provider-token scanning and targeted credential-context review established no likely live credential. Broader matching included embedded-image noise and an explicitly dummy tutorial parameter; values are omitted. This is not a complete PII/secret or disclosure-boundary audit. No sensitive value is intentionally compiled.

All pages are **draft** because package/dependency coverage and runtime/optional-backend verification remain incomplete. The ledger supports future idempotent ingestion: re-inspect missing or changed paths, reconcile the existing source identity, and update only new/corrected knowledge rather than duplicating concepts.

[^txtai-repo]: Revision `738aac4`: `README.md`; `CITATION.cff`; `LICENSE` header; `setup.py`; `src/python/txtai/version.py`; local Git HEAD/log/remote/status and tracked-path inventory inspected this session; implementation locators and precise evidence are distributed across the linked concepts and ledger. Reconciliation locators: `vectors/base.py::Vectors.tokens, prepare`, `vectors/dense/sbert.py::STVectors.encode`; `database/client.py::Client.createtables`, `database/rdbms.py::RDBMS.load, initialize`; `graph/rdbms.py::RDBMS.create, load`; `api/authorization.py::Authorization.digest`; `api/cluster.py::Cluster.run`; `api/application.py::createmcp`; `pipeline/llm/rag.py::RAG.reference`; `.github/workflows/build.yml`; `embeddings/base.py::Embeddings.defaultsparse`; `docs/embeddings/configuration/general.md`; `docs/cloud.md`, `docker/schedule/Dockerfile`. Short module paths are relative to `src/python/txtai/`. Coverage, AST and fingerprint results are session-generated checks over local artifacts, not upstream runtime verification.
