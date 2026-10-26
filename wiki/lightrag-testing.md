---
type: Concept
title: LightRAG testing, evaluation, and reproduction limits
description: Offline and PostgreSQL CI tiers, WebUI/build checks, external-model evaluation scripts, and the distinction between syntax checks and behavioral evidence.
tags: [operations, ml, testing, evaluation]
status: draft
created: 2026-10-26
generated: { by: llm-wiki-agent/1, at: 2026-10-26T08:55:00Z }
stale_after: 2027-01-24
sources:
  - id: lightrag-aaebfe1
    resource: ../raw/LightRAG/README.md
    scope: ../raw/LightRAG/
    kind: code
    revision: aaebfe1
    title: LightRAG repository
---

**Observed:** LightRAG configures separate offline Python, PostgreSQL smoke, setup-wizard, frontend and publication workflows, alongside server-backed RAGAS and paper-reproduction utilities. **Reproduced in this ingest:** 818 tracked Python files parsed successfully with standard-library `ast.parse` on Python 3.12.3/Linux; no upstream code was imported. **Limit:** syntax parsing does not establish imports, dependencies, passing tests, model quality or service correctness.[^lightrag-aaebfe1]

## CI intent, not CI results

| Surface | Configured check observed |
| --- | --- |
| Python tests | Python 3.12/3.14; frozen uv install; serial `pytest tests/ -m offline` |
| PostgreSQL smoke | PostgreSQL 18 service and opt-in PG table-graph smoke test |
| Setup wizard | Separate offline `tests/setup` run |
| Frontend | Bun install, TypeScript, lint, tests, build and bundle-budget enforcement |
| Lint | pre-commit over tracked files |
| Publication | Frontend build before wheel; release-version rewrite; PyPI trusted publishing and keyless image signing |

**Observed:** integration tests require explicit opt-in, and setup tests are separated from the main recursion surface. Inspected workflows do not execute full live integration matrices for every storage backend or render/lint the Helm chart. The test-artifact upload names a JUnit XML file without an observed command/config generating it. None of these workflow definitions proves a successful run at this revision.[^lightrag-aaebfe1]

## Evaluation surfaces

- **Observed:** `eval_rag_quality.py` uses RAGAS, a live LightRAG endpoint, external model credentials and evaluation extras, writing CSV/JSON results. It is not an offline deployment check.
- `offline_retrieval_check.py` implements a deterministic sample dataset/oracle retrieval check without a server; that limited sample mechanism is not a benchmark of production graph retrieval.
- Paper reproduction scripts form a separate context-preparation → insertion → question-generation → query → pairwise LLM-judge chain. UltraDomain data is external; question generation downloads a GPT-2 tokenizer if uncached and invokes a model; alternate scripts depend on a different vendor endpoint. Batch judging uploads data to the OpenAI Batch API.
- `Step_3.py` appends JSON output with an envelope per invocation; repeated runs can produce invalid concatenated JSON. Reproduction requires explicit output management, not an assumption of idempotent reruns.[^lightrag-aaebfe1]

## Reported benchmark boundaries

**Reported:** README/Reproduce tables compare LightRAG with other RAG methods using comprehensiveness, diversity, empowerment and overall judge preferences across domains. The snapshot did not supply inspected executed run logs/config/model pins sufficient for this ingest to reproduce those values. **Synthesis:** keep them as source-reported research claims, not evidence that this service configuration outperforms the other platforms in this wiki.[^lightrag-aaebfe1]

## What this compilation checked

The five Explore passes inspected selected implementation regions and selected assertion bodies, then the curator checked source identity, coverage, citation joins and wiki structure. No pytest/Bun test, live query, model/provider call, service/container build, database/Helm command, benchmark, security exploit or destructive maintenance command ran. Test names/assertions support test intent only.[^lightrag-aaebfe1]

## Relationships

- **Constrains claims in:** [Overview](lightrag.md), [retrieval](lightrag-retrieval.md), and [deployment](lightrag-deployment.md).
- **Related:** [RAG-Anything reproduction](rag-anything-reproduction-evaluation.md) has its own external-data/model protocol and is not the same experiment.
- **Uses:** [Source map and coverage ledger](lightrag-source-map.md) for pending inspection and reproducibility limits.

[^lightrag-aaebfe1]: Revision `aaebfe1`: `.github/workflows/{tests.yml,pg-smoke.yml,setup-tests.yml,webui-tests.yml,linting.yaml,pypi-publish.yml,docker-publish.yml}`; `pyproject.toml` pytest/extras configuration; `tests/conftest.py::pytest_addoption` and integration skip logic; `scripts/test.sh`; `lightrag/evaluation/{eval_rag_quality,offline_retrieval_check}.py`; `reproduce/{Step_0,Step_1,Step_1_openai_compatible,Step_2,Step_3,Step_3_openai_compatible,batch_eval}.py`; `docs/Reproduce.md`; README “Replicating Findings in the Paper”. Session syntax result was recorded in `outputs/lightrag-ingest/static-checks.json`, a disposable session artifact not retained in this repository; method `ast.parse` without imports; not an upstream verification event.
