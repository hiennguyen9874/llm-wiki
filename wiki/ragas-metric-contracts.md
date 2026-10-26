---
type: Concept
title: Ragas metric APIs and custom metric contracts
description: Legacy sample-scored metrics, collections metrics and custom keyword-scored metrics have different base classes and error contracts.
tags: [rag, ml, evaluation, api]
status: draft
created: 2026-10-26
generated: { by: llm-wiki-agent/1, at: 2026-10-26T09:20:38Z }
stale_after: 2027-01-24
sources:
  - id: ragas-298b682
    resource: ../raw/ragas/README.md
    scope: ../raw/ragas/
    kind: code
    revision: 298b682
    title: Ragas repository
---

**Observed:** Ragas has three scoring surfaces, not a single interchangeable metric API. Legacy concrete names remain importable from `ragas.metrics` through a deprecation shim; collections metrics are direct exports from `ragas.metrics.collections`; custom decorators and DiscreteMetric/NumericMetric/RankingMetric live in `ragas.metrics`. Only legacy Metric subclasses satisfy the type gate in `evaluate()`.[^ragas-298b682]

## Contract matrix

| Surface | Input | Result and model requirements |
| --- | --- | --- |
| Legacy Metric / SingleTurnMetric / MultiTurnMetric | Typed sample, declared columns | Numeric score; legacy model/wrapper ecosystem |
| Collections BaseMetric | `ascore(**kwargs)` | MetricResult; modern Instructor LLM and modern embedding interfaces when required |
| Custom decorators | Function parameters as keywords | Validated inputs and wrapped MetricResult; exceptions/validation failures become value=None with reason |
| DiscreteMetric / NumericMetric / RankingMetric | Prompt variables as keywords, LLM supplied per call | Structured output with allowed-value validator |

`ragas.metrics.BaseMetric` aliases SimpleBaseMetric, while `ragas.metrics.collections.BaseMetric` is a distinct subclass adding validation. Likewise collections' prompt BasePrompt is not the legacy prompt/base.py class. **Synthesis:** record fully qualified imports in experiment artifacts; matching short names do not establish API compatibility.[^ragas-298b682]

MetricResult carries value, optional reason and traces; `to_dict()` uses the `result` key, while its JSON hook uses `value`. Custom metric exception-to-None behavior differs from legacy executor NaN fallback and from collections methods that raise. Collections sync `score()` rejects use inside an active event loop; custom decorator sync paths have different nested-loop handling. Check results for None/NaN and use `ascore()` for async composition.[^ragas-298b682]

## Migration contradictions

The migration guide describes some APIs as removed, but the source still resolves legacy AspectCritic, SimpleCriteriaScore and AnswerSimilarity with deprecation warnings. The shim announces v1.0 as the removal target for its mapped metric names. Collections already exports multimodal metrics despite a guide statement that they remain unmigrated. Guide examples importing collections.Metric or faithfulness.util.FaithfulnessPrompt do not match the inspected exporters/symbols. This is observed documentation/code disagreement, not a claim that every old API remains compatible.[^ragas-298b682]

## Relationships and limits

- Used explicitly inside [experiments](ragas-experiments.md); the runner does not choose or score metrics automatically.
- Legacy classes remain the supported input contract for [deprecated evaluation](ragas-legacy-evaluation.md).
- See [RAG scoring mechanisms](ragas-rag-metrics.md) and [specialized metrics](ragas-specialized-metrics.md).
- No import compatibility matrix or scoring call was executed; source exporter inspection is not runtime dependency verification.

[^ragas-298b682]: Ragas `298b682`, `src/ragas/metrics/__init__.py::__all__/_DEPRECATED_METRICS/__getattr__`; `src/ragas/metrics/base.py::Metric/SingleTurnMetric/MultiTurnMetric/SimpleBaseMetric/SimpleLLMMetric`; `src/ragas/metrics/collections/base.py::BaseMetric._validate_llm/_validate_embeddings/score`; `src/ragas/metrics/decorator.py::create_metric_decorator`; `src/ragas/metrics/result.py::MetricResult`; `src/ragas/evaluation.py::aevaluate`; `docs/howtos/migrations/migrate_from_v03_to_v04.md::Metrics Migration/Removed Features`. Static inspection only unless explicitly stated otherwise; coverage and remaining limits: [source map](ragas-source-map.md).
