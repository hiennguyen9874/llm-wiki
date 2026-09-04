---
type: Concept
title: DeepLoop residual scaling for looped transformers
description: DeepLoop is a conservative Post-LN residual parameterization that raises the DeepNorm exponent to 1/2 for repeatedly visited shared blocks, supported by source-reported small and medium looped-LM and HRM experiments.
tags: [deepnorm, initialization, parameter-sharing, recurrent-depth, transformers]
status: stable
created: 2026-09-04
generated: { by: llm-wiki-agent/1, at: 2026-09-04T03:57:33Z }
sources:
  - id: li2026deeploop
    resource: ../raw/arXiv-2607.13491v2/main.tex
    title: "DeepLoop: Depth Scaling for Looped Transformers"
---

# DeepLoop residual scaling for looped transformers

DeepLoop adapts DeepNorm to looped Transformers by treating repeated reads and writes of a shared residual branch as an additional first-order stability risk. Under the source's conservative aligned-visit regime at fixed physical depth, it uses a post-normalized, branch-input-normalized block with $\alpha=(2N)^{1/2}$ and per-matrix initialization gain $\beta=(8N)^{-1/2}$, rather than DeepNorm's exponent $1/4$. Its experiments report better validation loss at loop counts above one, but the language-model comparisons are single-seed and do not directly measure the assumed cross-visit alignment.[^li2026deeploop]

## Mechanism and scope

- A looped stack of $K$ physical blocks run for $R$ rounds has unrolled depth $N=KR$ and $M=2N$ residual-sublayer visits. The source's block is $x_{i+1}=\mathrm{RMSNorm}(\alpha x_i+f_j(\mathrm{RMSNorm}(x_i);\phi_j))$; $\beta$ scales selected residual-branch weight matrices only at initialization, not each runtime branch output.[^li2026deeploop]
- The source models the first-order tied update as a sum of visit-wise read sensitivities times a sum of visit-wise gradient contributions for each shared parameter. Its visit-alignment coefficient $\kappa_R$ yields the sufficient condition $M\kappa_R(\beta/\alpha)^2=O(1)$. This is a source derivation conditional on its local-sensitivity assumption, not a general empirical law.[^li2026deeploop]
- For $\alpha=(cN)^p$, $\beta=(dN)^{-p}$, fixed $K$, and $\kappa_R=\Theta(R^\gamma)$, the derived threshold is $p\ge(1+\gamma)/4$: it recovers DeepNorm's $p=1/4$ for decorrelated visits and gives $p=1/2$ for fully aligned visits. DeepLoop keeps DeepNorm's decoder constants $c=2,d=8$ and uses the latter conservative setting.[^li2026deeploop]

## Reported evidence

- At 100,000 training steps on FineWeb-Edu 50B tokens, GPT-2-small (124M) and GPT-2-medium (350M) looped language models were effectively tied with a pre-LN baseline at $R=1$. In single-seed runs, DeepLoop had lower final validation loss at $R=3,5,7$ at both scales; the largest reported difference was -0.0278 nats for the medium model at $R=7$.[^li2026deeploop]
- On eight lm-evaluation-harness tasks, the medium model's mean accuracy at $R=7$ was 53.88% versus 52.95% (zero-shot) and 55.20% versus 54.62% (one-shot). At medium $R=5$ one-shot, however, the baseline led by 0.23 percentage points; task and loop-count results are therefore not uniformly favorable.[^li2026deeploop]
- A short GPT-2-small $R=3$ exponent sweep found training escape fractions of 0/5 through 2/5 for $p=0.30$--$0.45$, 3/5 at $p=0.50$, and 5/5 at $p=0.55$ and $0.60$. It brackets rather than precisely validates the proposed threshold, and is limited to one scale, loop count, and short training horizon.[^li2026deeploop]
- Applied to the source's Hierarchical Reasoning Model configuration, with 24 gradient-visible residual-sublayer visits under one-step gradient truncation, DeepLoop reported ARC-AGI-1 two-vote accuracy of 39.75% versus 36.50% for vanilla HRM. The source reports a four-seed control with about 0.5-point standard deviation, but this result remains source-specific.[^li2026deeploop]

## Limits and open checks

The language-model ablations alter both normalization/block parameterization and scaling relative to the pre-LN baseline; their exponent-isolation evidence is the smaller $p$-sweep. The central alignment variable $\kappa_R$ is not measured, and larger models, alternate normalization placements, longer training, and different physical-depth regimes are untested. The source's $p=1/2$ recommendation is thus a conservative rule under stated assumptions, not evidence that all looped models have aligned visits.[^li2026deeploop]

## Relationships

- Related to: [Loss scaling for looped language models](loss-scaling-for-looped-language-models.md) — both vary loop count in tied models, but DeepLoop targets residual-update stability while the other source fits performance scaling.
- Related to: [Controlled looped-model architecture ablations](controlled-looped-model-architecture-ablations.md) — both show that looped-model outcomes depend on parameterization choices beyond nominal unrolled depth.

[^li2026deeploop]: Li et al., *DeepLoop: Depth Scaling for Looped Transformers*, source manuscript, abstract; §§1--4; Table 1; Appendix “Empirical $p$-sweep at fixed loop count” (arXiv:2607.13491v2, 2026).