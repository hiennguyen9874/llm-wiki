---
type: Concept
title: Grokking for implicit reasoning
description: Extended training can yield in-distribution implicit rule application after training has already fit synthetic knowledge-reasoning data.
tags: [grokking, implicit-reasoning, parametric-memory, transformers]
status: stable
created: 2026-09-04
generated: { by: llm-wiki-agent/1, at: 2026-09-04T03:28:50Z }
sources:
  - id: wang2024grokked
    resource: ../raw/arXiv-2405.15071v3/neurips_2024.tex
    title: "Grokked Transformers are Implicit Reasoners: A Mechanistic Journey to the Edge of Generalization"
  - id: kohli2026loop
    resource: ../raw/arXiv-2604.07822v2/colm2026_conference.tex
    title: "Loop, Think, & Generalize: Implicit Reasoning in Recurrent-Depth Transformers"
---

# Grokking for implicit reasoning

In controlled synthetic knowledge-reasoning tasks, an 8-layer decoder-only transformer reached robust in-distribution rule generalization only after extended training beyond near-perfect training fit—a grokking phase.[^wang2024grokked]

## Evidence

- The study defines implicit reasoning as inducing and applying latent rules from atomic facts and inferred facts. Its in-distribution (ID) test holds out some inferences from the same atomic-fact distribution; its out-of-distribution (OOD) test uses a separate atomic-fact partition.[^wang2024grokked]
- For two-hop composition, training accuracy exceeded 99% around 14K optimization steps while ID generalization was then 9.2%; near-perfect ID accuracy emerged only after roughly 50 times as many training steps. OOD composition accuracy remained absent through 2 million steps in the reported setting.[^wang2024grokked]
- Increasing the training inferred-to-atomic fact ratio ($\phi$) accelerated ID generalization in both composition and comparison. Holding that ratio fixed while scaling entity count did not qualitatively change generalization behavior; the authors therefore propose data distribution, rather than absolute data size, as the relevant driver in these experiments.[^wang2024grokked]
- Higher weight decay accelerated grokking in an additional composition experiment, consistent with the paper's circuit-efficiency explanation.[^wang2024grokked]
- A later recurrent-depth study reports a three-stage version of this trajectory in a related two-hop task: training-set fit, delayed ID generalization, then delayed systematic OOD generalization over atomic facts never used in training compositions. Its logit-lens and activation-patching evidence associates the final stage with reusable bridge representations, but this is still a controlled synthetic result.[^kohli2026loop]

## Interpretation and limits

The paper hypothesizes that optimization first fits a higher-complexity memorizing circuit and later favors a more efficient generalizing circuit; this is a mechanistic interpretation supported by its controlled interventions, not a demonstrated law of training dynamics.[^wang2024grokked]

The evidence is from synthetic tasks, a fixed family of transformer setups, and selected tokenization and scaling variants. The authors explicitly caution that their rule-induction formulation does not cover all forms of reasoning or establish direct equivalence to practical language-model pretraining.[^wang2024grokked]

## Related concepts

- [Circuit organization and systematic generalization](circuit-organization-and-systematic-generalization.md) describes the proposed circuits and their connection to OOD behavior.
- [Parametric memory for complex reasoning](parametric-memory-for-complex-reasoning.md) covers the paper's large-search-space comparison task.
- [Recurrent-depth systematic generalization and extrapolation](recurrent-depth-systematic-generalization-and-extrapolation.md) covers the later three-stage finding and depth-extrapolation evidence.

[^wang2024grokked]: Wang, Yue, Su, and Sun, *Grokked Transformers are Implicit Reasoners: A Mechanistic Journey to the Edge of Generalization*, source manuscript, abstract and §§1–3 plus appendix (2024).
[^kohli2026loop]: Kohli, Parthasarathy, Sun, and Yao, *Loop, Think, & Generalize: Implicit Reasoning in Recurrent-Depth Transformers*, §§4--5 and appendix (arXiv:2604.07822v2, 2026).