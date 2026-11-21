---
type: Concept
title: Surrogate harness training
description: Training individual harness calls on synthetic task environments that preserve target solution strategies, sometimes with simulated sub-calls.
tags: [language-models, training, agents, synthetic-data]
status: draft
created: 2026-11-21
generated: { by: llm-wiki-agent/1, at: 2026-11-21T16:46:14Z }
sources:
  - id: compositional-harnesses
    resource: ../raw/LanguageModelHarnessesCanBeCompositionalGeneralizers/LanguageModelHarnessesCanBeCompositionalGeneralizers.md
    scope: ../raw/LanguageModelHarnessesCanBeCompositionalGeneralizers/
    kind: paper
    title: Language Model Harnesses Can Be Compositional Generalizers
---

Surrogate harness training targets a particular language-model call in an agent harness using an easier synthetic environment that preserves a desired solution strategy, rather than requiring full expensive real-task rollouts. Tools or sub-calls may be replaced by oracle responses during training; deployment uses real ones. It depends on transfer of the learned orchestration and on real sub-call reliability, not merely on success against the oracle. The paper's results below are **reported**, not independently reproduced.[^compositional-harnesses]

## Procedure

1. Inspect a separate task split and base-model trajectories to identify a candidate program or decomposition for a target task family; generate synthetic tasks that exercise the strategy with different content.
2. Optionally replace sub-calls with synthetic oracle answers. The paper does this for BrowseComp-Plus, ExpertLongBench and OBLIQ; other synthetic environments use real sub-model calls.
3. For RLM-27B, generate hinted trajectories, select using synthetic rewards and an LM judge, and supervised-fine-tune the model. Alternatively, train with RL on these environments without hints; this is a different intervention and produced different efficiency behavior.[^compositional-harnesses]

The authors report 8,015 root-only and 1,465 LongReason sub-agent synthetic rollouts for SFT on Qwen3.8-27B, full-parameter one-epoch training on an 8×H100 node. Synthetic environments were designed with knowledge of the target benchmark families and candidate solutions. They are not evidence of zero-shot transfer to unknown task families.[^compositional-harnesses]

## Evaluation and limits

On eight held-out benchmark splits, the paper reports the base Qwen3.8-27B in the same RLM harness at 46.1 average versus 58.5 for SFT RLM-27B: **12.4 percentage points**, or about 26.9% relative to the baseline. Per-task results vary: for example, OBLIQ rises 13.5→15.2, BrowseComp-Plus 64.8→64.9, and LooGLE 51.4→82.0. Synthetic-task RL instead reaches 52.9. Equal-weight suite averages conceal task heterogeneity; CTC itself averages distinct splits.[^compositional-harnesses]

Mean turns fall 18.4→6.5; root input tokens 263K→44K, and summed root plus sub-call input/output tokens approximately 721K→385K, based on rounded table averages. These are token counts, not end-to-end cost or latency guarantees. In measured synthetic rollouts, mean runtime was not always lower than the real task, including RLM-27B LongReason (39s versus 36s).[^compositional-harnesses]

Despite distinct source content and evaluation splits, task wording overlaps substantially in several synthetic environments: Appendix B.9 reports exact shared 13-word sequences for all evaluated CTC and ExpertLongBench descriptions and most LooGLE descriptions. The authors say CTC reuses generic task queries with different item collections; overlap alone does not establish contamination, but limits claims of novel task-description generalization. Some rollout selection uses an LM judge, and neither the synthetic generation nor benchmark results were independently checked.[^compositional-harnesses]

## Composing learned solvers recursively

The authors select 87 tasks on which the trained model performs well and the base model poorly, and construct 2,000 four-task gated chains. RLM-27B solves 55.2% of full chains in one root trajectory; a recursion hint alone reduces this to 47.2%, whereas additional recursion SFT reaches 77.5% (95% intervals ±2.2, ±2.2 and ±1.8 points respectively). Fresh nested harness instances and an 80-turn total versus 20-per-instance budget are part of the comparison. The selected task pool makes this a targeted composition test, not a general estimate for arbitrary tasks.[^compositional-harnesses]

## Relationships

- **Uses:** [Compositional generalization in LM harnesses](compositional-generalization-in-lm-harnesses.md) motivates training a local call that transfers to the real harness.
- **Synthesis:** [Training recursive language models](training-recursive-language-models.md) covers earlier root-trajectory distillation and RL approaches.
- **Uses:** [Recursive language models](recursive-language-models.md) are the harness used in these experiments.

## Coverage

The [source coverage ledger](compositional-generalization-in-lm-harnesses.md#source-and-coverage) describes the paper capture, inspected figures, pending attachments, and verification limits. Synthetic implementations, judge behavior, datasets and trained weights were not inspected or run. Draft status reflects these limits.[^compositional-harnesses]

[^compositional-harnesses]: [Paper](../raw/LanguageModelHarnessesCanBeCompositionalGeneralizers/LanguageModelHarnessesCanBeCompositionalGeneralizers.md), §§4.1–4.3, Tables 3–6 and Figure 6; Appendix A Table 7 and §A.4; Appendix B §§B.1, B.9–B.11, Tables 12–13 and Figure 9; `images/image-000009.jpg`.
