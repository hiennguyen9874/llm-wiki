---
type: Concept
title: Mamba-2 evaluation and efficiency
description: The Mamba-2 report gives competitive Pile language-model results, stronger associative recall with larger state, and hardware- and configuration-qualified SSD speed claims.
tags: [evaluation, efficiency, language-modeling, mamba, mamba-2, ssm]
status: stable
created: 2026-08-01
generated: { by: llm-wiki-agent/1, at: 2026-08-01T02:14:44Z }
sources:
  - id: dao-gu-2024
    resource: ../raw/arXiv-2405.21060v1/structure.tex
    title: "Transformers are SSMs: Generalized Models and Efficient Algorithms Through Structured State Space Duality"
---

# Mamba-2 evaluation and efficiency

The authors report that Mamba-2 matches or improves on Mamba and their Transformer++ baseline on Pile language modeling, while the SSD kernel is 2–8 times faster than Mamba's fused scan in their tested large-state benchmark and overtakes FlashAttention-2 at 2K tokens. These are reported architecture and kernel results, not universal performance guarantees.[^dao-gu-2024]

## Reported language-model results

Scaling experiments trained approximately 125M–1.3B models on the Pile at Chinchilla-style token counts and sequence length 8K. The reported curves place Mamba-2 below both Mamba and Transformer++ in validation perplexity across the tested compute range.[^dao-gu-2024]

For 2.7B-scale models trained on 300B Pile tokens with the GPT-NeoX tokenizer, Mamba-2 reported Pile validation perplexity 6.09 and a seven-task zero-shot average 60.2. The corresponding Mamba-2.8B results were 6.22 and 59.9; Pythia-2.8B's were 6.73 and 55.7. Cross-model comparisons remain qualified by model architecture and evaluation setup, although these entries share the reported dataset and tokenizer.[^dao-gu-2024]

On the synthetic multi-query associative recall task, Mamba-1 with state size 16 remained near zero accuracy at the two longer tested sequence lengths, while Mamba-2 improved with state size and reached near-perfect accuracy at sufficient model width. This supports state capacity and the Mamba-2 design on that synthetic task, not lossless arbitrary-context retrieval.[^dao-gu-2024]

## Hybrid attention evidence

In a controlled 350M, 48-layer Pile experiment, six attention layers among 48 gave the best reported validation perplexity (8.26), versus 8.60 for pure Mamba-2 and 8.68 for Transformer++. At 2.7B, a six-attention-layer Mamba-2 hybrid reported 5.95 Pile perplexity and 61.0 average zero-shot accuracy, compared with 6.09 and 60.2 for pure Mamba-2. The results support complementarity in these configurations; they do not establish a universal 10% attention-layer optimum.[^dao-gu-2024]

## Efficiency boundary

The speed figure uses an A100 80GB PCIe and state dimension 64. It shows SSD 2–8 times faster than the Mamba fused scan at tested long lengths and below FlashAttention-2's timing curve from 2K tokens onward; at 16K, the paper describes SSD as roughly six times faster than FlashAttention-2. The end-to-end Mamba-2 model can still lag a Transformer at short contexts because it replaces every layer with SSD, whereas the compared Transformer alternates attention and hardware-efficient MLP layers.[^dao-gu-2024]

## Relationships

- **Evaluates:** [Mamba-2 architecture and parallelism](mamba-2-architecture-and-parallelism.md) and its SSD layer.
- **Benchmarks:** [Structured State Space Duality](structured-state-space-duality.md)'s block algorithm.
- **Supports hybrid use of:** [Self-attention computational profile](self-attention-computational-profile.md), where periodic token-addressable retrieval complements fixed recurrent state.

## Evidence limits

All measurements are author-reported; no independent replication is available in this source bundle. The paper controls several Pile comparisons but cannot isolate the SSD kernel, block design, state size, tokenizer, and training recipe in every external baseline. The synthetic recall task and a single A100 kernel benchmark should not be generalized to arbitrary workloads or hardware.

[^dao-gu-2024]: Tri Dao and Albert Gu, “Transformers are SSMs: Generalized Models and Efficient Algorithms Through Structured State Space Duality,” arXiv:2405.21060v1, [source](../raw/arXiv-2405.21060v1/structure.tex), Sections 9–10 and experimental-details appendix.