---
type: Concept
title: Loop-boundary early exit in looped language models
description: A controlled study finds that exits at repeated-stack boundaries preserve quality better than arbitrary intermediate exits, but reports theoretical FLOP savings rather than end-to-end speed.
tags: [adaptive-computation, early-exit, inference, parameter-sharing, transformers]
status: stable
created: 2026-09-04
generated: { by: llm-wiki-agent/1, at: 2026-09-04T03:31:47Z }
sources:
  - id: lee2026sparse
    resource: ../raw/arXiv-2605.09165v2/main.tex
    title: "Sparse Layers are Critical to Scaling Looped Language Models"
---

# Loop-boundary early exit in looped language models

A controlled looped-transformer study reports that training-free, entropy-threshold exits at loop boundaries offer better reported perplexity-versus-skipped-FLOPs trade-offs than an untied Base model allowed to exit at any layer. The authors attribute this to boundary hidden states passing through the same output-facing layers as the final state, but the evidence is limited to model outputs and theoretical compute savings rather than causal intervention or measured serving throughput.[^lee2026sparse]

## Evaluation and findings

- At each candidate exit, the study projects the hidden state through the final layer norm and LM head, then exits a token when vocabulary-distribution entropy is below a swept threshold. Looped models may exit only after a full pass through their shared stack; Base and unlooped MoE may exit after any intermediate layer.[^lee2026sparse]
- For compute-optimal $10^{18}$-FLOP models, 10% nominal FLOPs saved yielded reported perplexity of 50.2 for dense Looped and 51.0 for Looped-MoE, versus 55.4 for Base and 75.7 for MoE. Thus, sparse experts alone did not produce the favorable early-exit trade-off.[^lee2026sparse]
- With 16 effective layers and fixed width, increasing Looped-MoE configurations from $8\times2$ to $4\times4$ and $2\times8$ provided progressively better reported trade-off curves. At 10% savings, their perplexities were 51.0, 44.3, and 42.0, respectively; the non-looped MoE baseline reported 75.7.[^lee2026sparse]

## Evidence for the proposed mechanism

The authors project every intermediate hidden state to vocabulary space and calculate normalized Jensen--Shannon divergence from the final output distribution. In looped models, the fraction of tokens below their 0.5 convergence threshold jumps at the first loop boundary, unlike Base at the same effective depth. This supports the architectural account that a repeated stack's boundary is output-facing, but it does not isolate that property from other effects of looping or establish a sufficient deployment mechanism.[^lee2026sparse]

## Trust boundary and deployment limit

The outcomes are perplexity and nominal unused-depth FLOPs on source-controlled test tokens, not end-to-end latency, throughput, memory, or quality under an optimized inference engine. Entropy thresholds may also have different calibration and quality trade-offs under other models, tasks, decoding policies, loop depths, or hardware. The source explicitly leaves throughput validation for future work.[^lee2026sparse]

## Relationships

- Uses: [Sparse MoE for looped language-model scaling](sparse-moe-for-looped-language-model-scaling.md) — the same controlled comparison provides the Looped-MoE configurations and routing analysis.
- Related to: [Ouro looped language models](ouro-looped-language-models.md) — both exploit repeated-depth exit points, but Ouro learns a per-token exit distribution whereas this study uses no exit training and evaluates only nominal compute savings.

[^lee2026sparse]: Lee et al., *Sparse Layers are Critical to Scaling Looped Language Models*, source manuscript, §§3--5, appendix, and Table 4 (arXiv:2605.09165v2, 2026).