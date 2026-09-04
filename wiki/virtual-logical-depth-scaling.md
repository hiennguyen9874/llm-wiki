---
type: Concept
title: Virtual logical depth scaling
description: Repeating transformer layers with tied weights can increase effective computation depth at fixed parameter count; the source reports improved reasoning metrics while its random-sequence memory proxy remains nearly unchanged.
tags: [parameter-sharing, reasoning, scaling-laws, transformers]
status: stable
created: 2026-09-04
generated: { by: llm-wiki-agent/1, at: 2026-09-04T03:16:22Z }
sources:
  - id: zhu2025vld
    resource: ../raw/arXiv-2506.18233v3/main.tex
    title: "Beyond Parameters: Exploring Virtual Logic Depth for Scaling Laws"
---

# Virtual logical depth scaling

Virtual logical depth (VLD) is the extra effective depth created by reapplying transformer layers with shared weights, without adding unique parameters. In the paper's controlled experiments, VLD improved several reported reasoning metrics while a random-sequence entropy measure of memorization stayed nearly fixed at a given parameter count; these are source-specific findings, not an established general scaling law.[^zhu2025vld]

## Mechanism

- The paper defines VLD as effective algorithmic depth minus the number of base layers. It reuses standard transformer layers rather than introducing new layer parameters.[^zhu2025vld]
- It evaluates three tying schedules: **sequence** (repeat adjacent layers), **cycle** (repeat a block in its original order), and **inverse cycle** (repeat that block in reverse order).[^zhu2025vld]
- Reuse increases inference/training computation through additional layer applications even though the parameter count is unchanged. It therefore differs from token-wise test-time scaling.[^zhu2025vld]

## Reported evidence

- For GPT-2 models trained from scratch on synthetic iGSM tasks, the 4-layer base achieved 46.3% at 15 operations. The reported cycle pattern rose to 70.7% at its listed $\times5$ VLD setting; sequence and inverse-cycle configurations also generally improved with the tested depth settings.[^zhu2025vld]
- On 20- and 21-operation distribution shifts, the 4-layer cycle results at listed $\times5$ were 43.8% and 40.2%, respectively, versus 21.8% and 21.2% for the base model.[^zhu2025vld]
- After LoRA fine-tuning from the same LLaMA-3.2-3B-Instruct weights on a 2.3B-token multi-domain corpus, the source reports Cycle-VLD improvements over its base variant on Math500 (35.40 vs. 30.40), GPQA (32.32 vs. 29.80), AIME (6.67 vs. 3.33), HumanEval pass@1 (39.52 vs. 37.79), and MBPP pass@1 (40.22 vs. 38.36).[^zhu2025vld]
- The capacity result uses the reduction in output entropy when memorizing a 640,000-token IID random-number sequence (vocabulary size 50,257) as its knowledge-capacity proxy. Across 5M and 20M GPT-2 models, the figure reports this proxy as nearly stable across reuse patterns and depths, whereas it increases with parameter count in non-VLD baselines.[^zhu2025vld]

## Trust boundary and limitations

The capacity proxy measures fitted random-token information, not factual knowledge retrieval or knowledge usefulness. The reasoning evidence covers the paper's selected GPT-2 synthetic task and one LoRA fine-tuning comparison, so it does not establish that layer tying will improve arbitrary models, tasks, or production systems.[^zhu2025vld]

Scaling is not strictly monotonic in the reported results: for example, the 4-layer cycle configuration at $\times3$ scored 61.6% at 15 operations, slightly below 62.1% at $\times2$. The authors identify extreme-depth behavior, optimal tying patterns, and multi-seed statistics as open work; the synthetic table averages 2--3 checkpoints after convergence rather than reporting multi-seed uncertainty.[^zhu2025vld]

[^zhu2025vld]: Zhu et al., *Beyond Parameters: Exploring Virtual Logic Depth for Scaling Laws*, source manuscript, abstract, §§3--5, and appendices (arXiv:2506.18233v3, 2025).