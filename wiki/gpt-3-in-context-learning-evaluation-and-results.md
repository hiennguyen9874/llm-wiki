---
type: Concept
title: GPT-3 in-context learning evaluation and results
description: GPT-3 evaluates zero-, one-, and few-shot task behavior through text-only conditioning and completion scoring, reporting scale-sensitive but task-dependent gains without weight updates.
tags: [gpt-3, in-context-learning, few-shot-learning, prompting, evaluation]
status: stable
created: 2026-07-31
generated: { by: llm-wiki-agent/1, at: 2026-07-31T15:42:00Z }
sources:
  - id: brown-gpt-3-2020-v4
    resource: ../raw/arXiv-2005.14165v4/main.tex
    title: Language Models are Few-Shot Learners
---

# GPT-3 in-context learning evaluation and results

The GPT-3 report evaluates task behavior without fine-tuning: zero-shot prompts contain only a natural-language instruction, one-shot prompts add one solved demonstration, and few-shot prompts add as many demonstrations as fit. Across the reported benchmarks, larger models and more demonstrations usually help, but results vary substantially by task and do not demonstrate that the model learns wholly new tasks at inference time.[^brown-gpt-3-2020-v4]

## Evaluation protocol

For each evaluation item, few-shot prompting randomly draws $K$ task-training examples as context plus completion, then presents the target context. The fixed 2,048-token window usually permits 10–100 demonstrations; the authors select among candidate $K$ values on development data where available. This means reported few-shot results depend on prompt formatting, randomly drawn examples, context capacity, and development-set selection.[^brown-gpt-3-2020-v4]

For multiple-choice tasks, the report selects the completion with the highest conditional likelihood, usually normalized per token; for ARC, OpenBookQA, and RACE it additionally divides by an answer-context likelihood. Free-form tasks use beam search with width 4 and length penalty $0.6$. These are task-specific evaluation constructions, not a uniform interface for measuring general capability.[^brown-gpt-3-2020-v4]

## Reported behavior

The source reports broadly smooth improvement in validation loss and in many downstream measures over model scale. It specifically finds that few-shot gains grow faster than zero-shot gains in its aggregate benchmark view, which it interprets as increasing proficiency with in-context examples rather than as proof of an internal learning mechanism.[^brown-gpt-3-2020-v4]

Results were mixed. On closed-book TriviaQA, the 175B model reports 64.3% zero-shot, 68.0% one-shot, and 71.2% few-shot accuracy; on SuperGLUE, it reports near-leading few-shot results for COPA and ReCoRD but chance-level 49.4% on WiC. It also reports weak results on adversarial NLI and some reading-comprehension formats, despite strong gains on selected cloze, QA, and translation evaluations.[^brown-gpt-3-2020-v4]

Synthetic tasks offer suggestive but limited evidence of adaptation. For example, few-shot accuracy is high for short addition and subtraction but declines sharply as operands grow; zero-shot character-manipulation performance is generally low, while more demonstrations and scale improve several artificial transformations. The authors explicitly leave unresolved whether in-context behavior is de novo task learning, recognition of tasks encountered in pretraining, or a mixture that varies by task.[^brown-gpt-3-2020-v4]

## Relationships

- **Evaluates:** [GPT-3 scaled causal language model](gpt-3-scaled-causal-language-model.md) without parameter updates.
- **Extends:** [GPT-2 zero-shot multitask evaluation and overlap auditing](gpt-2-zero-shot-multitask-evaluation-and-overlap-auditing.md) by explicitly distinguishing zero-, one-, and few-shot settings and systematically varying model scale.
- **Qualified by:** [GPT-3 benchmark contamination audit](gpt-3-benchmark-contamination-audit.md), which identifies reported scores requiring leakage caveats.

[^brown-gpt-3-2020-v4]: Tom B. Brown et al., “Language Models are Few-Shot Learners,” arXiv:2005.14165v4 (2020), bundled [LaTeX source](../raw/arXiv-2005.14165v4/main.tex), especially Sections 1–3, 3.2, 3.7–3.9, and 5.
