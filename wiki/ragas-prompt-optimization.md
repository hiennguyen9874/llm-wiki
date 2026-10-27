---
type: Concept
title: Ragas prompt lifecycle and metric optimizers
description: Typed prompt adaptation and persistence differ from genetic and DSPy optimization of annotated legacy metric prompts.
tags: [ml, rag, prompts, optimization]
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

**Observed:** Ragas supports prompt inspection/replacement, language adaptation and JSON persistence, plus separate genetic and DSPy-based optimization of metric instructions against annotated examples and a loss. **Synthesis:** translating a testset prompt, optimizing a legacy judge and customizing a collections prompt are different operations; capability does not transfer automatically across these APIs.[^ragas-298b682]

## Prompt lifecycle

Legacy/testset PydanticPrompt stores typed input/output, instructions and examples. PromptMixin get/set operations identify prompts by `prompt.name`, not necessarily their containing attribute name. Adaptation returns replacements that callers apply explicitly; instruction translation is optional. Save/load use language-qualified JSON names, with existing-file/directory constraints and version warnings.[^ragas-298b682]

PydanticPrompt's BaseRagasLLM route uses output parsing/repair retries, whereas Instructor/raw LangChain branches directly validate returned JSON in the inspected dispatch. Collections uses another BasePrompt abstraction. **Synthesis:** retry/translation/persistence semantics should be checked for the concrete prompt and model path, not assumed from the name “prompt.”[^ragas-298b682]

## Optimizer boundary

| Optimizer | Mechanism | Observed constraints |
| --- | --- | --- |
| GeneticOptimizer | Instruction induction, feedback mutation, crossover and fitness scoring | Metric and LLM required; minimum 10 annotations; defaults population 3 and sample size 12; mutates live metric instructions |
| DSPyOptimizer | Optional DSPy MIPROv2 instruction/demonstration search | Validates parameters; defaults include auto light and seed 9; requires optional DSPy dependency |

Optimizer operates on metric-bound SingleMetricAnnotation and Loss and returns prompt-name-to-instruction mappings. This is not an automatic optimizer for testset query synthesizers or all collections metrics. Translation/localization is the inspected testset customization route.[^ragas-298b682]

## Relationships and limits

- Used by legacy [metric training](ragas-metric-contracts.md); [testset generation](ragas-testset-generation.md) uses adaptation/replacement rather than this optimizer contract.
- Depends on [model adapters](ragas-model-adapters.md); extra search can incur judge/provider calls.
- Genetic/DSPy implementations were read in selected material regions, not exhaustively. No optimizer ran; no improvement, convergence, cost, fairness or held-out generalization result is claimed. Annotation acceptance and evaluation splits require caller review.

[^ragas-298b682]: Ragas `298b68274234`, `src/ragas/prompt/mixin.py::PromptMixin.get_prompts/set_prompts/adapt_prompts/save_prompts/load_prompts`; `src/ragas/prompt/pydantic_prompt.py::PydanticPrompt.generate_multiple/adapt`; `src/ragas/prompt/base.py::BasePrompt.save/load`; `src/ragas/optimizers/base.py::Optimizer`; `src/ragas/optimizers/genetic.py::GeneticOptimizer`; `src/ragas/optimizers/dspy_optimizer.py::DSPyOptimizer`; `src/ragas/metrics/base.py::MetricWithLLM.train`; `tests/unit/test_optimizer_config.py`. Static inspection only unless explicitly stated otherwise; coverage and remaining limits: [source map](ragas-source-map.md).
