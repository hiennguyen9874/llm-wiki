---
type: Concept
title: Hindsight decision models
description: Hindsight's small open-weight models (hs-decide-1-flash, hs-rerank-1, hs-embed-1) that replace LLM judgments inside recall, consolidation, reflect and pages.
tags: [agent-memory, hindsight, models, cost]
status: draft
created: 2026-11-06
generated: { by: llm-wiki-agent/1, at: 2026-11-06T16:50:00Z }
sources:
  - id: readme
    resource: ../raw/hindsight/README.md
    scope: ../raw/hindsight/
    kind: code
    revision: eb963cb
    title: Hindsight README (monorepo root)
  - id: decision-doc
    resource: ../raw/hindsight/hindsight-docs/docs/developer/decision-models.mdx
    kind: documentation
    revision: eb963cb
    title: Decision models developer doc
  - id: models-blog
    resource: ../raw/hindsight/hindsight-docs/blog/2026-11-03-hindsight-models.md
    kind: article
    revision: eb963cb
    title: Introducing Hindsight Models
  - id: decision-code
    resource: ../raw/hindsight/hindsight-api-slim/hindsight_api/engine/decision_model.py
    kind: code
    revision: eb963cb
    title: DecisionModel provider abstraction
---

A **decision model** answers the many small judgments inside a memory system (is this fact new, which memories matter, could this change a page) with a typed answer instead of text, so far fewer calls reach the main LLM. When enabled, recall ranking, consolidation triage, reflect orchestration and knowledge-page delta refresh use it.[^readme][^decision-doc] Status is `draft` because all performance figures are vendor-reported and not independently reproduced.

## Models (Reported)

| Model | Role | Size | License |
| --- | --- | --- | --- |
| `hs-decide-1-flash` | Typed judgments for recall, consolidation, reflect, pages | 0.8B | Apache 2.0 |
| `hs-rerank-1` | Reranker | 114M | MIT |
| `hs-embed-1` | 384-dimension embeddings | 112M | MIT |

All three read eight languages and are on Hugging Face (`hindsight-ai`) or hosted on Hindsight Inference (about $0.02/M input tokens for the decision model, per docs). Enable hosted use via `hindsight-admin cloud login` and `HINDSIGHT_API_DECISION_MODEL_PROVIDER=hindsight`.[^readme][^decision-doc] As of 1.2.0, `hs-rerank-1` is the default reranker (see [providers](hindsight-llm-embedding-providers.md)).

## Behaviour

- Safe to lose everywhere except recall, where the decision model *is* the ranker; its order is final, with no cross-encoder score published.[^decision-doc] See [Recall](hindsight-recall-pipeline.md).
- Code: `engine/decision_model.py::DecisionModel`, providers `none | hindsight | typesafe | cloudflare | openai`, default `none`. Docs say only `hindsight` and `typesafe` are supported for reflect and pages (Observed vs Reported; the extra provider names are not documented for those uses).[^decision-code][^decision-doc]

## Claims (Reported by vendor, not reproduced)

- Median decision-model request 167 ms vs 1–7 s for an LLM call; 3.1 vs 4.5 LLM calls per case.[^models-blog]
- 2.5× cheaper, 1.9× less model-call time, +2.2 points on one flash LLM; another flash model within 2 points at 19× less cost.[^models-blog]
- Consolidation triage −40% LLM calls; see [Consolidation](hindsight-consolidation-and-mental-models.md).[^decision-doc]

## Relationships

Used by [Reflect](hindsight-reflect-agent.md), [Recall](hindsight-recall-pipeline.md), [Consolidation](hindsight-consolidation-and-mental-models.md). Evaluation harness: [Benchmarks and testing](hindsight-benchmarks-and-testing.md).

[^readme]: `README.md` § "Decision Models".
[^decision-doc]: `hindsight-docs/docs/developer/decision-models.mdx` (models, providers, where used, safe-to-lose notes).
[^models-blog]: `hindsight-docs/blog/2026-11-03-hindsight-models.md` (TL;DR and latency sections).
[^decision-code]: `hindsight-api-slim/hindsight_api/engine/decision_model.py::DecisionModel`; `config.py::DEFAULT_DECISION_MODEL_PROVIDER`.
