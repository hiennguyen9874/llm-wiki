---
type: Concept
title: txtai operations and testing
description: Python packaging, configuration, Docker and Lambda deployment surfaces, CI intent, documentation drift, and unexecuted validation.
tags: [operations, txtai, testing, deployment]
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

**Observed:** txtai packages a Python library with optional feature extras; one application configuration can drive local Python composition, FastAPI serving, one-shot workflows, scheduled workflows, or an AWS Lambda adapter. Deployment artifacts and CI define intended operating procedures, not a verified successful deployment of this snapshot.[^txtai-repo]

## Installation and configuration

`setup.py` declares Python ≥3.11 and version `9.15.0`. Normal installation includes the default numerical/model/index dependencies; extras add agents, API, databases, graphs, vector adapters, pipelines, workflows, and development tooling. Setting `MINIMAL` changes the distribution to `txtai_minimal` and moves default dependencies into a `default` extra. The `all` extra aggregates feature dependencies; it is not needed for every use case.[^txtai-repo]

`Application.read` accepts a dict, YAML string, or file path. Configuration chooses embeddings, pipelines, agents, workflows, persisted index path, and optional cluster. Dependent pipelines (`similarity`, `extractor`, `rag`, `reranker`) are initialized after the initial pipeline pass. Application mutations use an `RLock` and require `writable`; reindex additionally requires `reindex`. These are operation/configuration gates, not tenant authorization.[^txtai-repo]

The documented basic service invocation is `CONFIG=app.yml uvicorn "txtai.api:app"`. `CONFIG` locates configuration; `TOKEN` enables the built-in hashed-bearer check. `DEPENDENCIES`, `EXTENSIONS`, and `API_CLASS` resolve trusted Python integration classes; treat them as executable configuration, not user-supplied data. See [API](txtai-api.md) and [security](txtai-security.md).[^txtai-repo]

## Deployment surfaces

| Artifact | Intended role |
| --- | --- |
| `docker/base/Dockerfile` | CPU/GPU build arguments, optional-component installation, native libraries and NLTK assets |
| `docker/minimal/Dockerfile` | Minimal-distribution base |
| `docker/api/Dockerfile` | Uvicorn bound to all interfaces |
| `docker/workflow/Dockerfile` | One-shot workflow |
| `docker/schedule/Dockerfile` | Long-running scheduled workflows via `wait` |
| `docker/aws/Dockerfile`, `api.py`, `workflow.py` | Lambda runtime client; API variant uses Mangum |

API/workflow/schedule/AWS images instantiate `API('config.yml', False)` at build time to cache model assets. This can require network/model access during image construction; it is not evidence that all runtime inputs are baked in. Pin and review images, models, and credentials for an actual deployment.[^txtai-repo]

**Reported:** `docs/observability.md` describes an external `mlflow-txtai` plugin and `mlflow.txtai.autolog()` for examples tracing extractors, embeddings, RAG, workflows, and agents. The plugin and its remote screenshots were not inspected; tracing coverage and overhead are unverified.[^txtai-repo]

## Test and CI intent

- **Observed:** `make data` downloads the v6.2.0 release test archive into `/tmp`; shared test utilities use `/tmp/txtai`. `make test` runs `unittest discover`; `make coverage` runs discovery per module filter and combines coverage data.
- **Observed:** the build workflow runs Python 3.11/Java 21 on Ubuntu, macOS, and Windows, installs `.[all,dev]`, prepares NLTK data, then runs `make data coverage`. **The 100% coverage failure threshold and pre-commit step are Ubuntu-only**, not separate confirmed gates on every OS.
- **Observed:** minimal-package CI checks importability; documentation CI deploys MkDocs. Optional-dependency tests simulate missing modules; embeddings tests instantiate real models and therefore depend on external assets. The sampled MCP test checks route presence, not end-to-end authorization/protocol correctness.
- **Reproduced, session syntax check only:** all 409 tracked Python files passed `ast.parse` on Python 3.12.3/Linux. No txtai module was imported, and no application tests, builds, services, provider calls, or benchmark ran.[^txtai-repo]

## Documentation and portability cautions

- **Observed:** `docs/cloud.md` references `docker/service/Dockerfile`, absent from the pinned tree; the inspected scheduler artifact is `docker/schedule/Dockerfile`. Do not follow the stale path without reconciliation.
- **Observed:** packaging allows `torch>=2.4`, while macOS CI pins `2.12.1` and the base Dockerfile pins `2.14.1+cpu`. These are different environment constraints, not proof of incompatibility or equivalent behavior.
- **Observed:** direct pipeline `safeopen` defaults differ from Application/API defaults; see [security](txtai-security.md). Configuring a Python pipeline directly is not the same trust boundary as serving it through `Application`.[^txtai-repo]

## Relationships and limits

- **Configures:** [Architecture](txtai-architecture.md), [API/cluster](txtai-api.md), and [agents/workflows](txtai-agents-workflows.md).
- **Depends on:** [Security](txtai-security.md) for transport, executable configuration, and filesystem/network safeguards.
- **Part of:** [txtai](txtai.md); incomplete static coverage is recorded in the [source map](txtai-source-map.md).

No compatibility verification, deployment smoke test, container build, actual CI result, resource sizing, or performance evidence is available from this ingest.

[^txtai-repo]: Revision `738aac4`: `setup.py` default dependencies, extras, `MINIMAL`, `setup`; `src/python/txtai/version.py`; `src/python/txtai/app/base.py::Application.read, createpipelines, index, reindex, function, resolvetask, wait`; `src/python/txtai/api/application.py::create, lifespan`; `README.md` “Why txtai?” and “Installation”; all six `docker/*/Dockerfile` artifacts listed above; `docker/aws/api.py`, `docker/aws/workflow.py`; `docs/cloud.md` scheduling/service example; `docs/observability.md` Initialization and examples; `Makefile::data, test, coverage`; `.coveragerc`; `.github/workflows/build.yml::jobs.build`, `minimal.yml`, `docs.yml`; `.pre-commit-config.yaml`; `test/python/utils.py::Utils.PATH`, `test/python/testoptional.py`, `test/python/testembeddings.py::TestEmbeddings.setUpClass`, `test/python/testapi/testmcp.py`. Session AST result is recorded in `outputs/txtai-ingest/syntax-check.json`; that result is not an upstream behavioral claim.
