---
type: Concept
title: SMELT compute-matched MoE looped transformers
description: SMELT loops the middle half of a sparse MoE transformer twice while closely matching FLOPs, stored parameters, and KV cache, reporting lower validation loss and 6.8–18.0% frontier compute savings within its fitted range.
tags: [attention-sinks, mixture-of-experts, parameter-sharing, scaling-laws, transformers]
status: stable
created: 2026-09-04
generated: { by: llm-wiki-agent/1, at: 2026-09-04T03:45:19Z }
sources:
  - id: wang2026smelt
    resource: ../raw/arXiv-2609.01343v1/paper.tex
    title: "SMELT: Scaling Laws for Compute-Matched MoE Looped Transformers"
---

# SMELT compute-matched MoE looped transformers

SMELT (Sparse MoE Transformer, middle layers Loop Twice) is a source-reported recipe for partially tied decoder-only MoE transformers: repeat the middle 50% of physical layers twice while narrowing width, adding experts, and changing attention geometry to closely match an untied baseline's per-token FLOPs, non-embedding parameter count, and KV cache. Across its internal-data grid, the paper reports lower loss in every matched cell and 6.8–18.0% compute savings at a common fitted frontier loss for budgets from $10^{20}$ to $10^{21}$ FLOPs; these are source-run, model-family-specific results, not a general proof that depth recurrence is superior.[^wang2026smelt]

## Recipe and matching

- Models use top-8 sparse MoE feed-forward layers and grouped-query attention. SMELT repeats a contiguous middle half of the stack twice, scales each repeated residual update by $1/2$, narrows hidden width to pay for the extra executions, adds experts to recover stored parameters, and adjusts head size/GQA ratio for KV-cache parity.[^wang2026smelt]
- In the reported 200M ablations, validation loss was lowest near a 50% loop span at both tested sparsity levels; a 12-physical-/18-effective-layer model was best in its depth sweep; and two visits beat three or four in the stated matched-FLOP setup. The DCLM Core ranking did not always track validation loss in the span sweep, so the authors selected the span using validation loss; every configuration was trained once.[^wang2026smelt]
- The matching targets are close, not exact: the source reports typical residual differences below 4% for measured per-token training FLOPs and KV cache, and below 1% for total parameters. Its compute-equivalent sparsity label is based on FLOPs relative to a fully active control; consequently, a looped configuration labelled $S=0$ can still route sparsely to a larger expert pool.[^wang2026smelt]

## Reported scaling and downstream evidence

- The grid crosses four active-parameter scales (100M, 200M, 600M, and 1.6B) with one dense-reference and three sparse levels, reaching 54B non-embedding stored parameters at the largest, most sparse configuration. Separate six-parameter loss surfaces were fitted only to the 72 endpoints per architecture at the three sparse levels, over $1.3\times10^{19}$–$2.2\times10^{21}$ cumulative training FLOPs; the $S=0$ controls were excluded as a distinct regime.[^wang2026smelt]
- At $10^{20}$ FLOPs, the source's fitted compute-optimal frontiers give SMELT a 6.8–10.0% compute-efficiency gain across sparsity levels; at $10^{21}$, 14.7–18.0%. Its $10^{22}$ values are explicitly extrapolations beyond the fitted range, with broad bootstrap intervals, and should not be treated as measured scaling evidence.[^wang2026smelt]
- SMELT won 96/96 matched pairs on DCLM Completion and 83/96 on DCLM Core. On the subset of 30 MMLU pairs where the baseline was at least 10 points above chance, it won 29. A calibration against baseline validation loss found favorable downstream residuals, but this is an analysis fit to the paper's own baseline endpoints rather than an independent evaluation.[^wang2026smelt]
- The source reports the largest category-level frontier gain on Code (20.4% at $10^{21}$ FLOPs and $S\approx95\%$), and a 1.52-fold larger normalized improvement for 512–4096-token samples than for 32–256-token samples. In a separate few-shot sweep, the mean gap over 16 tasks rises from 0.9 percentage points at zero-shot to 1.9 points when demonstrations are available.[^wang2026smelt]

## Proposed second-pass behavior

On a held-out sample, the paper observes substantial cross-visit overlap in selected experts and attended tokens, but larger and directionally aligned visit-two residual updates. It reports cross-visit Q/K cosine similarity of 0.89–0.93 versus 0.65–0.74 for V, and 56–66% top-8 attended-token overlap. A Dyck-language case study and general-sample probes associate the second visit with lower segment-start attention-sink mass and more attention to relevant demonstration answers. These descriptive probes are compatible with a refinement interpretation, but do not causally establish that any observed mechanism produces the scaling or benchmark gains.[^wang2026smelt]

## Trust boundary and limitations

The authors use a proprietary transformer family, an internal pretraining corpus, and source-run evaluations; the complete architecture and training stack are not released. The data and implementation therefore limit replication and portability.[^wang2026smelt]

The design ablations are only at the 200M active-parameter scale, so the selected span and two-visit count may not remain optimal at larger scales. Budget matching covers arithmetic FLOPs, parameter count, and KV-cache size—not end-to-end latency or hardware efficiency, which may be worse with serial re-execution and sparse routing. The mechanism probes are observational, and no independent replication is reported.[^wang2026smelt]

## Relationships

- Related to: [Sparse MoE for looped language-model scaling](sparse-moe-for-looped-language-model-scaling.md) — both report that sparse expert layers can make tied recurrence competitive, but SMELT uses a larger, three-budget-matched scaling grid while the other study holds effective depth and FLOPs in a smaller controlled regime.
- Contrasts with: [Loopie layer-loop compute-matched MoE scaling](loopie-layer-loop-compute-matched-moe-scaling.md) — SMELT loops a middle block and closely matches FLOPs, parameters, and KV cache; Loopie repeats each layer locally and selects comparisons by measured optimizer-step time.

[^wang2026smelt]: Wang et al., *SMELT: Scaling Laws for Compute-Matched MoE Looped Transformers*, source manuscript, abstract and §§1–7, appendices, figures, and tables (arXiv:2609.01343v1, 2026).