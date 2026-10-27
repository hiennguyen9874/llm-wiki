---
type: Concept
title: Ragas framework adapters and tracing boundaries
description: Evaluation adapters, message conversion, uploads and tracing are separate surfaces with legacy schema drift and placeholder implementations.
tags: [rag, operations, integrations, tracing]
status: draft
created: 2026-10-26
generated: { by: llm-wiki-agent/1, at: 2026-10-26T09:28:37Z }
stale_after: 2027-01-24
sources:
  - id: ragas-298b682
    resource: ../raw/ragas/README.md
    scope: ../raw/ragas/
    kind: code
    revision: 298b68274234
    title: Ragas repository
---

**Observed:** Ragas integrates with other frameworks through evaluation wrappers, message/trace conversion, remote endpoint invocation, uploads and tracing SDKs. These are not one uniform integration contract. Some still target deprecated evaluation/schema APIs, and some tracing helpers are placeholders rather than verified remote retrieval.[^ragas-298b682]

## Adapter families

| Surface | Observed boundary |
| --- | --- |
| LangChain / LlamaIndex | Evaluation/model wrappers; many compatibility paths retain legacy metric/sample contracts |
| Bedrock / Griptape / Swarm / R2R | Inspected adapters convert messages, traces, RAG contexts or search results to Ragas evaluation structures; not a hosted application runtime |
| AG-UI | Can invoke caller-supplied endpoint with HTTPX and follow redirects; requires explicit network trust |
| LangSmith | Testset upload/evaluation through ambient SDK client; upload helper expects historical question/ground_truth columns |
| Opik | Tracer forwards through Opik integration SDK |
| Langfuse / MLflow | Optional tracing wrappers with different implementations, described below |

**Synthesis:** check exact adapter input/output schemas and metric namespace before adopting a framework recipe; a newer Testset using user_input/reference is not proven compatible with a helper hard-coding historical field names. Authentication, backend endpoints and data capture for enabled SDKs require separate review.[^ragas-298b682]

## Tracing implementation discrepancies

- Langfuse `sync_trace` obtains an ID, then constructs a placeholder trace with empty observations/scores instead of fetching trace details. `LangfuseTrace.filter` returns an empty list. Thus its “wait for sync” docstring does not establish populated remote data; constructor/SDK compatibility was not run.
- MLflow `sync_trace` actually calls trace APIs and errors when no trace exists; URL generation requires MLFLOW_HOST.
- Helicone config/header machinery exists, but inspected internal call sites only set evaluation session fields; no caller of `default_headers()` or automatic client rerouting was found. Setting that config alone does not establish proxy logging in this snapshot.

Representative tracing unit tests use mocked SDKs. Those assertions are not hosted-service verification and do not prove trace content completeness.[^ragas-298b682]

## Relationships and limits

- Uses [legacy evaluation](ragas-legacy-evaluation.md) and [dataset schemas](ragas-datasets.md) in older adapters.
- Depends on optional extras and [operations](ragas-operations.md); [security](ragas-security.md) distinguishes default analytics from enabled integration payloads.
- AG-UI and some wrappers were inspected at structural/network-call depth only. No framework app, upload, remote trace fetch or service integration ran; end-to-end interoperability remains unverified.

[^ragas-298b682]: Ragas `298b68274234`, `src/ragas/integrations/langchain.py`; `llama_index.py`; `amazon_bedrock.py`; `griptape.py`; `swarm.py`; `r2r.py`; `ag_ui.py` (HTTPX client/network-call regions); `langsmith.py::upload_dataset/evaluate`; `opik.py`; `tracing/langfuse.py::sync_trace/LangfuseTrace.filter`; `tracing/mlflow.py::sync_trace/MLflowTrace.get_url`; `helicone.py::HeliconeSingleton.default_headers` (integration paths relative to `src/ragas/integrations/`); `src/ragas/evaluation.py::aevaluate`; `tests/unit/integrations/test_tracing.py`. Static inspection only unless explicitly stated otherwise; coverage and remaining limits: [source map](ragas-source-map.md).
