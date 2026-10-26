---
type: SourceMap
title: Ragas source map and coverage
description: Pinned Ragas identity, artifact-level inspection ledger, draft coverage gaps and syntax-only validation limits.
tags: [rag, operations, provenance, source-map]
status: draft
created: 2026-10-26
generated: { by: llm-wiki-agent/1, at: 2026-10-26T09:28:37Z }
stale_after: 2027-01-24
sources:
  - id: ragas-298b682
    resource: ../raw/ragas/README.md
    scope: ../raw/ragas/
    kind: code
    revision: 298b68274234c060deacab3cf5fb52aa3a20e885
    title: Ragas repository
---

**Observed:** this compilation pins VibrantLabs Ragas at `298b68274234c060deacab3cf5fb52aa3a20e885`, using four parallel Explore subagents for architecture/datasets/runners, metrics/model interfaces, synthetic data/prompts, and operations/integrations/security, plus curator reconciliation, targeted source rereading and a separate focused semantic review. The entire 694-path tracked inventory is accounted for in a [per-file coverage ledger](ragas-source-coverage.tsv). **Limit:** this is a targeted static ingest, not exhaustive implementation or runtime verification; concepts remain draft.[^ragas-298b682]

## Source identity

| Field | Inspected value |
| --- | --- |
| Canonical entry point | `raw/ragas/README.md` |
| Package scope | `raw/ragas/` |
| Revision | `298b68274234c060deacab3cf5fb52aa3a20e885` |
| Git description | `v0.4.3-8-g298b682` (not an installed distribution version) |
| Commit date / subject | `2026-02-23T23:47:18-08:00` / fix: allow fork contributors in check-docs CI workflow (#2606) |
| Upstream remote | `git@github.com:vibrantlabsai/ragas.git` |
| License / runtime | Apache-2.0 header; Python >=3.9 manifest |
| Snapshot status | Clean source worktree at initial and post-compilation checks; tracked-content fingerprint unchanged |

SCM generates distribution version; no package was built/imported to determine the installed version. Full license terms and third-party license closure were not audited. English implementation/docs predominate in the inspected files; no translation-parity claim.[^ragas-298b682]

## Retrieval map

- [Ragas agent, SQL, lexical and multimodal metrics](ragas-specialized-metrics.md) — Rule-based tool and citation checks coexist with LLM goal/SQL judges, CSV result comparison and network-capable multimodal scoring.
- [Ragas dataset stacks and sample schemas](ragas-datasets.md) — Backend-bound Dataset and Experiment tables coexist with legacy EvaluationDataset samples and are not interchangeable.
- [Ragas evaluation framework](ragas.md) — Code-grounded overview of Ragas experiments, evaluation metrics, synthetic test generation, and its role alongside RAG platforms.
- [Ragas experiment runner and versioning](ragas-experiments.md) — Experiment row functions run in completion order with backend inheritance, dropped failures, and optional repository-mutating versioning.
- [Ragas framework adapters and tracing boundaries](ragas-integrations.md) — Evaluation adapters, message conversion, uploads and tracing are separate surfaces with legacy schema drift and placeholder implementations.
- [Ragas installation, CLI and test operations](ragas-operations.md) — Python packaging, uv workspace, template scaffolding and CI checks coexist with unfinished CLI evaluation contracts and unexecuted provider-dependent suites.
- [Ragas legacy evaluation and executor](ragas-legacy-evaluation.md) — Deprecated evaluate and aevaluate retain sample validation, metric fan-out, ordered scores, cancellation, and optional cost tracing.
- [Ragas metric APIs and custom metric contracts](ragas-metric-contracts.md) — Legacy sample-scored metrics, collections metrics and custom keyword-scored metrics have different base classes and error contracts.
- [Ragas model adapters, prompts and caching](ragas-model-adapters.md) — Client-supplied structured LLMs and dual embedding interfaces drive scores, while shared cache keys can omit model-instance configuration.
- [Ragas persistence backends](ragas-backends.md) — Plugin-discovered CSV, JSONL, in-memory and Google Sheets backends have distinct durability and type-preservation constraints.
- [Ragas prompt lifecycle and metric optimizers](ragas-prompt-optimization.md) — Typed prompt adaptation and persistence differ from genetic and DSPy optimization of annotated legacy metric prompts.
- [Ragas retrieval and answer-quality metrics](ragas-rag-metrics.md) — RAG judges measure context support, generated-question relevance, ranked precision, attribution recall and reference-based correctness with distinct limits.
- [Ragas synthetic testsets and query synthesis](ragas-testset-generation.md) — Graph-compatible query distributions combine personas, styles and single/multi-hop contexts to produce single-turn references without exact-size or quality guarantees.
- [Ragas synthetic-test knowledge graph](ragas-testset-graph.md) — Length-dependent transforms build document/chunk property graphs whose summary and entity relationships feed query synthesis.
- [Ragas telemetry and evaluation trust boundaries](ragas-security.md) — Default analytics, enabled data sinks, asymmetric image access, local paths, plugins and credential-handling patterns define Ragas trust boundaries.

## Coverage ledger and dependency closure

| Disposition | Artifacts | Meaning |
| --- | ---: | --- |
| Targeted static | 238 | Substantive file regions, signatures or symbols inspected; depth varies, not full-file assurance |
| Inventory only | 1 | Empty sdk.py identified, no implemented behavior inferred |
| Excluded | 30 | Community/editor/agent guidance, housekeeping, CSS/font/favicon or identified branding; no runtime/measurement claims |
| Pending | 425 | Unread bodies, tests, docs, notebooks, data/plots/screenshots or ancillary scripts; Python syntax alone is separate |
| Total | 694 | One ledger row per tracked artifact |

All 33 tracked testset implementation artifacts were reported read by the generation explorer; the merged ledger conservatively marks even these targeted rather than pretending uniform depth across agents. Other implementation areas include selected datasets/evaluator/executor, backends, metric APIs and core metric bodies, model factories/providers, prompt/optimizer regions, integrations/tracing, CLI, analytics, CI and representative tests. Test-name/symbol inspection is not full assertion auditing. Agent report path lists and curator notes preserved inspection provenance in session outputs under `outputs/ragas-ingest/`; those outputs were disposable and are not retained, so that per-agent provenance is no longer re-auditable from this repository.

**Material dependency limits:** external provider SDK behavior, Instructor/LiteLLM compatibility, LangChain version resolution, HuggingFace/tiktoken assets, optional DSPy/Google/tracing/database-comparison libraries and their transitives were not independently inspected or installed. External docs/issues/papers and hosted services were not retrieved. Dataset/notebook cell content, plots and benchmark screenshots remain pending where the ledger says so; no empirical claim is extracted from them. Generated Markdown mirrors and original notebooks were not proven semantically equivalent.

**Visual coverage:** full images inspected for KG construction, scenario conditioning, generation/evaluation split and component-wise metrics. `docs/_static/architecture.png` is an AWS restaurant-agent example, not Ragas internals. Other images/plots remain pending or are explicitly excluded branding; no chart's numeric results were compiled. Historical field names in diagrams do not supersede current code schemas.[^ragas-298b682]

## Checks actually performed

**Reproduced, compilation-session only:** all 387 tracked Python files passed standard-library `ast.parse` under Python 3.12.3/Linux. This reads source text without importing upstream modules; it establishes syntax, not runtime compatibility, test outcomes or correctness. Full per-file results were written to `outputs/ragas-ingest/static-checks.json`, a disposable session artifact not retained in this repository.

A selected private-key/provider/AWS/GitHub token-shape screen across UTF-8 tracked content returned no matches; explorer-reviewed assignment matches were placeholders/fixtures. This is not exhaustive secret/PII detection, and unread notebook cells remain a privacy-review limit. No credentials or sensitive source values are reproduced in concepts.

Tracked-content inspection fingerprint: `03cd1b167bc713b06e65cfe74ee0e2ffc970e41b8f62c5718b3b18c7d74a8c36` (SHA-256 over sorted path bytes, NUL and each raw file's SHA-256 digest bytes). This is a session fingerprint, not signed upstream attestation.

A focused semantic review (recorded in the disposable `outputs/ragas-ingest/semantic-review.md`, not retained here) sampled the compiled claims against source and checked locators, citation joins, index descriptions and inventory/fingerprint consistency. Its graph-append/idempotency wording, precommit lint scope, distribution-heading locator and adapter-description corrections were applied. This is static synthesis review, not independent verification of runtime behavior.

No upstream tests, imports, builds, notebooks, benchmarks, containers, cloud/provider calls, model downloads, exploit attempts or Git-versioning helper ran. Structural/citation checks on compiled pages are repository-maintenance checks and do not verify Ragas behavior.

## Known gaps and follow-up

- Reproduce row-failure accounting/concurrency and invalid-score handling before regression gating.
- Test matching dataset/metric/runner namespaces under resolved dependencies; reconcile stale migration and CLI recipes.
- Validate graph-transform coverage and realized query/persona/hop distribution on representative mixed-length corpora.
- Audit unresolved rubric/summary/entity/topic/adaptor bodies and all pending artifacts before claiming exhaustive capability coverage.
- Test cache isolation by provider/model/prompt/schema; inspect installed cache serialization separately.
- Review untrusted image URLs/files, storage names, provider egress and CI secret/token trust with deployment-specific controls.
- Verify actual tracing data and legacy upload field compatibility; placeholder/mock intent is not remote-service validation.

## Idempotency

Source identity is normalized `raw/ragas/` plus this revision; all supporting files reconcile to this package and canonical README, not separate source records. Before re-ingest, find every concept declaring this scope/revision and compare ledger rows, snapshot fingerprint, new evidence and newly connected knowledge. Repeating covered evidence is a no-op; pending rows are explicit follow-up, not asserted complete coverage.

[^ragas-298b682]: Ragas `298b68274234c060deacab3cf5fb52aa3a20e885`, `README.md::Key Features/Installation/Open Analytics/Cite Us`; `pyproject.toml::project/build-system/tool.setuptools_scm`; `LICENSE` (Apache-2.0 header); `src/ragas/testset/`; `docs/_static/imgs/kg_rag.png/scenario_rag.png/ragas_workflow_white.png/component-wise-metrics.png` (whole diagrams); `docs/_static/architecture.png` (whole AWS example diagram). Static inspection only unless explicitly stated otherwise; coverage and remaining limits: [source map](ragas-source-map.md).
