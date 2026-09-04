---
type: Concept
title: Sparse MoE for looped language-model scaling
description: A controlled isoFLOP study finds that sparse MoE feed-forward layers close the scaling deficit of tied looped transformers, with routing differences across loop passes providing a proposed mechanism.
tags: [mixture-of-experts, parameter-sharing, scaling-laws, transformers]
status: stable
created: 2026-09-04
generated: { by: llm-wiki-agent/1, at: 2026-09-04T03:45:19Z }
sources:
  - id: lee2026sparse
    resource: ../raw/arXiv-2605.09165v2/main.tex
    title: "Sparse Layers are Critical to Scaling Looped Language Models"
---

# Sparse MoE for looped language-model scaling

In a controlled 16-effective-layer isoFLOP study, replacing tied looped transformers' dense FFNs with top-2-of-8 MoE layers made Looped-MoE outperform the dense untied Base model on reported test loss and Core 9 accuracy while storing fewer parameters. Dense looping remained worse than Base, and unlooped MoE achieved the lowest test loss, so the evidence supports sparse FFNs as a remedy for this source's looped-scaling deficit—not a general dominance of looping or Looped-MoE.[^lee2026sparse]

## Architecture and comparison

- The study compares Base (16 unique dense layers), Looped (8 dense layers applied twice), MoE (16 unique sparse layers), and Looped-MoE (8 sparse layers applied twice). All use the same active-parameter count at matched widths and tokens; active MoE parameters count only the two selected experts, whereas stored counts include all eight.[^lee2026sparse]
- Models use decoder-only Transformers and top-2 token-choice routing among eight SwiGLU experts. The authors apply load-balancing and router z-losses, and use a width-scaled $\mu$P variant that they report transfers the selected small-width learning rate with at most 0.8% loss difference in a four-effective-layer test.[^lee2026sparse]
- At four budgets from $5\times10^{16}$ to $10^{18}$ FLOPs on a 10B-token FineWeb-Edu sample, the ordering of fitted isoFLOP test losses was MoE, Looped-MoE, Base, then Looped. The reported loss exponents for Base and Looped-MoE were 0.076 and 0.077, respectively; their relative advantage is primarily an offset in the reported range rather than a clearly different scaling slope.[^lee2026sparse]
- At $10^{18}$ FLOPs, Looped-MoE reported Core 9 accuracy of 39.6 with 216M stored parameters, versus Base's 38.7 with 246M and dense Looped's 37.4 with 168M. The unlooped MoE had the lowest reported test loss but scored 36.4 on that benchmark average, a source hypothesis attributes this discrepancy to narrower per-token expert access.[^lee2026sparse]

## Proposed mechanism and limits

For the $8\times2$ Looped-MoE model, the authors compare each token's two selected experts across passes through a physical layer. In layers 1--6 and 8, 25--53% of tokens had disjoint expert sets and 4--14% had an exact match; most shared one expert. This is consistent with loop-specific subnetwork selection, but it is correlational routing analysis rather than an intervention showing that divergence causes the scaling result.[^lee2026sparse]

The study uses models up to 305M active and 711M stored parameters, fixed effective depth during width scaling, a FineWeb-Edu sample, and source-run OLMES evaluations. Its authors have not validated the fit by extended pretraining at 1B or 7B scales. Consequently, the results do not establish frontier-scale behavior, depth scaling, or a general downstream advantage for Looped-MoE.[^lee2026sparse]

## Relationships

- Related to: [Loss scaling for looped language models](loss-scaling-for-looped-language-models.md) — both report that dense tied looping trails an untied matched-depth baseline, though they use different regimes and scaling formulations.
- Related to: [Mixture-of-Recursions adaptive token computation](mixture-of-recursions-adaptive-token-computation.md) — both combine recurrence and routing, but this study uses sparse expert selection to restore expressivity rather than routing tokens to different recurrence depths.
- Enables: [Loop-boundary early exit in looped language models](loop-boundary-early-exit-in-looped-language-models.md) — the study evaluates its Looped-MoE models with training-free exits.
- Related to: [SMELT compute-matched MoE looped transformers](smelt-compute-matched-moe-looped-transformers.md) — both report sparse MoE as a way to make tied recurrence competitive, but SMELT uses a larger scaling grid and closely matches FLOPs, stored parameters, and KV cache.

[^lee2026sparse]: Lee et al., *Sparse Layers are Critical to Scaling Looped Language Models*, source manuscript, abstract, §§2--5, appendix, and Tables 1--4 (arXiv:2605.09165v2, 2026).