---
type: Concept
title: Ragas evaluation framework
description: Code-grounded overview of Ragas experiments, evaluation metrics, synthetic test generation, and its role alongside RAG platforms.
tags: [rag, ml, evaluation, architecture]
status: draft
created: 2026-10-26
generated: { by: llm-wiki-agent/1, at: 2026-10-26T09:20:38Z }
stale_after: 2027-01-24
sources:
  - id: ragas-298b682
    resource: ../raw/ragas/README.md
    scope: ../raw/ragas/
    kind: code
    revision: 298b68274234
    title: Ragas repository
---

**Observed:** Ragas is a Python evaluation library with two public workflow families: experiment functions over backend-bound data tables, and deprecated sample/metric evaluation over typed evaluation datasets. Its repository also provides synthetic RAG test-data generation, model adapters, prompts, integrations and CLI scaffolding. **Synthesis:** it complements a RAG application's retrieval/generation pipeline rather than replacing that application's document store, serving API or retriever.[^ragas-298b682]

## Feature and architecture map

| Concern | Retrieval entry |
| --- | --- |
| Row execution, concurrency and failure accounting | [Experiment runner](ragas-experiments.md) |
| Dataset naming, schemas and compatibility | [Dataset stacks](ragas-datasets.md) |
| Old evaluation, batching, cancellation and costs | [Legacy evaluation](ragas-legacy-evaluation.md) |
| Storage adapters and round-trip constraints | [Persistence backends](ragas-backends.md) |
| Scoring APIs and extensibility | [Metric contracts](ragas-metric-contracts.md) |
| Retrieval, grounding and answer-quality judges | [RAG metrics](ragas-rag-metrics.md) |
| Agent/tool, SQL and other metric families | [Specialized metrics](ragas-specialized-metrics.md) |
| Model clients, prompts and caching | [Model adapters](ragas-model-adapters.md) |
| Document graph and scenario synthesis | [Synthetic testsets](ragas-testset-generation.md) |
| Prompt adaptation and optimization | [Prompt optimization](ragas-prompt-optimization.md) |
| Framework traces and adapter boundaries | [Integrations](ragas-integrations.md) |
| Installation, CI, CLI and validation | [Operations](ragas-operations.md) |
| Telemetry, uploads and executable inputs | [Security](ragas-security.md) |
| Revision, full artifact inventory and limits | [Source map](ragas-source-map.md) |

**Observed stack:** Python >=3.9; setuptools/setuptools_scm; Pydantic 2, NumPy, HuggingFace datasets, OpenAI/Instructor, LangChain, NetworkX/scikit-network, diskcache and Typer/Rich. Optional extras add framework adapters, tracing, cloud storage and optimization dependencies. Package version is SCM-derived; this compilation pins the commit instead of assuming a semantic release.[^ragas-298b682]

## Interpretation and limits

The README's “objective metrics” and integration claims are **Reported**, not independently measured capability. Judge scores are conditional on prompts, models, available references and input schemas. Synthetic testsets are not verified ground truth merely because a generation pipeline produced them. All pages are draft because implementation, documentation and test coverage are targeted, not exhaustive. No benchmark or production-readiness conclusion was reproduced.[^ragas-298b682]

[^ragas-298b682]: Ragas `298b68274234`, `README.md::Key Features/Quickstart/Open Analytics`; `pyproject.toml::project/build-system/project.optional-dependencies`; `src/ragas/__init__.py::__all__`; `docs/_static/imgs/ragas_workflow_white.png` (full diagram, historical field names). Static inspection only unless explicitly stated otherwise; coverage and remaining limits: [source map](ragas-source-map.md).
