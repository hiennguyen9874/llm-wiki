---
type: Concept
title: GPT-3 benchmark contamination audit
description: GPT-3’s report uses conservative n-gram overlap tests and clean-subset evaluation to qualify web-scale benchmark leakage, while documenting a failed pre-training filter and residual uncertainty.
tags: [gpt-3, data-contamination, benchmark-leakage, evaluation, provenance]
status: stable
created: 2026-07-31
generated: { by: llm-wiki-agent/1, at: 2026-07-31T15:42:00Z }
sources:
  - id: brown-gpt-3-2020-v4
    resource: ../raw/arXiv-2005.14165v4/main.tex
    title: Language Models are Few-Shot Learners
---

# GPT-3 benchmark contamination audit

The GPT-3 report treats benchmark leakage from web-scale pretraining as a material qualification. It attempted pre-training removal, later found that filter was incomplete, and used conservative exact n-gram overlap plus clean-subset evaluation to identify results that should be caveated or withheld; the method cannot prove that the retained clean subset has the same distribution as the full benchmark.[^brown-gpt-3-2020-v4]

## Prevention failure and post-hoc test

The initial filter searched development and test data for normalized 13-gram matches, removed the matching span and a 200-character window, and discarded short fragments or heavily split documents. A bug caused the procedure to fail on long documents, including books; retraining was judged infeasible. The report consequently omits several almost-completely overlapping Wikipedia language-modeling benchmarks and the Children’s Book Test.[^brown-gpt-3-2020-v4]

For post-hoc analysis, the authors use Apache Spark to calculate exact collisions between benchmark items and the full pretraining corpus. Each example is marked dirty if it has any match at a dataset-specific $N$-gram length—normally the fifth-percentile example length, bounded between 8 and 13 words—or clean if it has none. Comparing the clean-only score with the full score tests for an association with detected overlap, not whether a model memorized answers.[^brown-gpt-3-2020-v4]

## Findings and limits

Potential overlap was often high, but the report finds no apparent overall correlation between contamination rate and performance change. Manual review found many false positives where training data contained a source passage or news text but not an answer-bearing question–answer pair. Small retained clean subsets also make score shifts unstable and may differ systematically in difficulty from removed items.[^brown-gpt-3-2020-v4]

The report flags PIQA (29% marked dirty; about a 3-point absolute drop on the clean subset) and Winograd (132 schemas found in training data; a 2.6-point drop) with asterisks. It notes substantial LAMBADA overlap but little clean/full difference, and excludes the fully overlapping language-modeling benchmarks rather than presenting an unreliable correction. These findings qualify particular historical scores; they do not establish that other evaluations are leakage-free.[^brown-gpt-3-2020-v4]

## Relationships

- **Audits:** [GPT-3 scaled causal language model](gpt-3-scaled-causal-language-model.md)'s web-scale training corpus.
- **Qualifies:** [GPT-3 in-context learning evaluation and results](gpt-3-in-context-learning-evaluation-and-results.md)'s benchmark claims.
- **Extends:** [GPT-2 zero-shot multitask evaluation and overlap auditing](gpt-2-zero-shot-multitask-evaluation-and-overlap-auditing.md) with exact overlap calculation and clean-subset comparisons.

[^brown-gpt-3-2020-v4]: Tom B. Brown et al., “Language Models are Few-Shot Learners,” arXiv:2005.14165v4 (2020), bundled [LaTeX source](../raw/arXiv-2005.14165v4/main.tex), especially Sections 2.2, 4, and Appendix C.
