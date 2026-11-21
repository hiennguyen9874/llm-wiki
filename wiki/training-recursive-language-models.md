---
type: Concept
title: Training recursive language models
description: Distillation and reinforcement-learning experiments for improving models operating recursive language-model scaffolds.
tags: [language-models, training, long-context]
status: draft
created: 2026-11-21
generated: { by: llm-wiki-agent/1, at: 2026-11-21T16:46:14Z }
sources:
  - id: rlm-paper-v3
    resource: ../raw/arXiv-2512.24601v3/main.tex
    scope: ../raw/arXiv-2512.24601v3/
    kind: paper
    revision: arXiv-2512.24601v3
    title: Recursive Language Models
---

The RLM paper reports small-scale training experiments that improve a model's ability to operate a [recursive language model](recursive-language-models.md) scaffold. Its central hypothesis is that improving root-level REPL orchestration can be useful even when leaf calls remain general-purpose models. These results are **reported**, not independently reproduced.[^rlm-paper-v3]

## RLM-Qwen3-8B distillation

The authors collected 2,250 candidate Qwen3-Coder-480B-A35B RLM trajectories over 750 English LongBenchPro tasks, using Qwen3-8B sub-calls. They removed zero-score and one-turn trajectories, leaving 1,072 candidates, split root turns into supervised examples, filtered long turns, and programmatically fixed common output-format errors. Training used prime-rl, batch size 64, 300 steps and 48 H100 hours. The main text summarizes the filtered set as 1,000 trajectories; the appendix's 1,072 is an intermediate post-filter count, not necessarily a contradiction.[^rlm-paper-v3]

The training plot reports Qwen3-8B RLM before versus after fine-tuning: CodeQA 26 to 32, BrowseComp+ 2 to 14, OOLONG 24 to 32.04, and OOLONG-Pairs 4.26 to 5.17, all percentages. The comparison is to the base model *in an RLM scaffold*, not the much stronger GPT-5 RLM. Generalization and faster execution are authors' reported observations, not guarantees.[^rlm-paper-v3]

## RL and length generalization

Separately, Qwen3-4B-Instruct-0527 was RL-trained on MRCRv2's 32k–64k token, two-needle split for 150 steps, batch size 128 and four rollouts per example, with a 4,096 output-token per turn limit and 20 iterations. Evaluation every 50 steps used the 512k–1M, eight-needle split; the plotted evaluation reward rises across checkpoints. This is one synthetic task and does not demonstrate general length extrapolation across all tasks.[^rlm-paper-v3]

## Relationships

- **Synthesis:** [Surrogate harness training](surrogate-harness-training.md) extends root-focused training with task-specific synthetic environments and sometimes simulated sub-calls.
- **Synthesis:** [Compositional generalization in LM harnesses](compositional-generalization-in-lm-harnesses.md) studies when learned orchestration transfers to longer or structurally related tasks.

## Limits

Training data, execution environments and evaluation were not independently inspected or rerun; the [package coverage ledger](recursive-language-models.md#source-and-coverage) records pending figures and other limits. The paper's evaluations and comparisons are detailed in [RLM evaluation and benchmarks](rlm-evaluation.md).[^rlm-paper-v3]

[^rlm-paper-v3]: [Paper source](../raw/arXiv-2512.24601v3/main.tex), abstract; `sections/sec4-results.tex` §§Methods and Results, Figure training plots; `appendix/sec5-training.tex` §§training and MRCRv2; `figures/training-plot-gem.png` panels a–b.
