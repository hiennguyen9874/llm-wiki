---
type: Concept
title: LoopFormer elastic-depth looped transformers
description: LoopFormer conditions each repeated transformer pass on normalized time and step size, using shortcut-consistency training to support user-selected global loop budgets without retraining.
tags: [adaptive-computation, elastic-depth, latent-reasoning, parameter-sharing, transformers]
status: stable
created: 2026-09-04
generated: { by: llm-wiki-agent/1, at: 2026-09-04T03:55:19Z }
sources:
  - id: jeddi2026loopformer
    resource: ../raw/arXiv-2602.11451v1/main.tex
    title: "LoopFormer: Elastic-Depth Looped Transformers for Latent Reasoning via Shortcut Modulation"
---

# LoopFormer elastic-depth looped transformers

LoopFormer is a decoder-only looped transformer whose shared $k$-block stack is conditioned on both its normalized trajectory time and the current step size. It trains a maximum-length route and a sampled shorter route together, with a stop-gradient consistency target, so a user can choose a sequence-level budget $M\leq L$ and trajectory at inference; this is a fixed global budget, not learned instance- or token-level allocation.[^jeddi2026loopformer]

## Design and training

- A trajectory has positive step sizes $\Delta_1,\ldots,\Delta_M$ that sum to one. At pass $i$, LoopFormer receives cumulative time $t_{i-1}$ and $\Delta_i$; sinusoidal-feature MLPs embed both scalars, and their sum controls RMSNorm scales and the MHSA/FFN residual gates.[^jeddi2026loopformer]
- The objective combines next-token losses for the maximum $L$-step trajectory and a sampled shortcut of length $S\in\{1,\ldots,L-1\}$ with a stop-gradient consistency term; the source sets both auxiliary weights to 0.1.[^jeddi2026loopformer]
- The manuscript describes the consistency term inconsistently: surrounding prose calls it an alignment of shorter- and longest-route logits, while its displayed objective and training algorithm align hidden states. The source artifact does not resolve which implementation was used.[^jeddi2026loopformer]
- The reported setup trains GPT-style models with $k\in\{1,2,3\}$ and $L\in\{8,12,24\}$ for about 25B Pile tokens. The shortcut route requires expected training FLOPs of roughly 1.5 times fixed-loop training, and the authors report about a 1.3-times wall-clock slowdown on four H100 GPUs; inference loop FLOPs scale with the selected $M$.[^jeddi2026loopformer]

## Reported results and diagnostics

For the $(3\otimes8)$ configuration at the 24x effective-compute budget, LoopFormer reports Pile/FineWeb-Edu/OpenWebText perplexities of 10.28/22.87/21.98 and mean accuracy of 44.81% across ten zero-shot tasks. The matched 24-layer Base reports 9.49/20.70/20.08 and 45.27%, while fixed TMLT reports 10.38/22.87/21.99 and 44.69%; the results therefore show competitiveness with fixed looped baselines, not superiority over the matched untied model.[^jeddi2026loopformer]

At reduced 12x and 6x budgets, LoopFormer reports mean task accuracy of 43.73% and 40.36%, respectively, versus 44.93% and 42.73% for the corresponding untied Base models. It outperforms the listed early-exit loop baselines in perplexity at 12x but not consistently at 6x, so the evidence supports nontrivial truncated operation rather than a general compute-quality advantage.[^jeddi2026loopformer]

The source's curvature, anisotropy, prompt-entropy, and CKA plots show greater cross-pass state change for LoopFormer than its depth-elastic early-exit baselines. These are diagnostic correlations: they show that representations differ across steps under the authors' metrics, but do not demonstrate that the modulation or the observed dynamics cause reasoning quality.[^jeddi2026loopformer]

## Trajectory selection and limits

In exhaustive discrete schedule tests, equal-budget routes vary by about 1.4 perplexity and 1.3 zero-shot-accuracy points for $(3\otimes8)$ at $M=4$; for $(2\otimes12)$ at $M=6$, the reported perplexity spread is nearly 3. The best schedules in those tests usually make larger jumps early and finer ones later, but this is an empirical result for the tested models and schedules, not a learned scheduling policy or universal rule.[^jeddi2026loopformer]

The evaluation is pretraining-scale (roughly 1B-parameter untied reference), uses a deduplicated Pile subset, three perplexity sets, and ten zero-shot benchmarks. It does not establish behavior for larger, instruction-tuned, long-context, or production-served models. The source also identifies global rather than instance/token-adaptive budgeting, multi-route training overhead, and correlational representation analysis as limitations.[^jeddi2026loopformer]

## Relationships

- Contrasts with: [Mixture-of-Recursions adaptive token computation](mixture-of-recursions-adaptive-token-computation.md) — LoopFormer accepts a user-selected sequence-level trajectory, whereas Mixture-of-Recursions learns token-specific recursion routing and defines specialized KV-cache policies.
- Related to: [Loop-boundary early exit in looped language models](loop-boundary-early-exit-in-looped-language-models.md) — both seek lower looped-model compute, but LoopFormer trains trajectory-conditioned short routes while the other study evaluates training-free entropy exits at loop boundaries.

[^jeddi2026loopformer]: Jeddi, Ciccone, and Taati, *LoopFormer: Elastic-Depth Looped Transformers for Latent Reasoning via Shortcut Modulation*, source manuscript, abstract, §§1–5, appendix, Tables 1–3, and local figure attachments (arXiv:2602.11451v1, 2026).