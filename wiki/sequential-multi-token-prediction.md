---
type: Concept
title: Sequential multi-token prediction
description: Sequential multi-token prediction trains additional causal modules to predict future tokens through a maintained causal chain, improving training signal density and optionally supplying speculative-decoding proposals.
tags: [pretraining, multi-token-prediction, speculative-decoding, language-modeling]
status: stable
created: 2026-08-01
generated: { by: llm-wiki-agent/1, at: 2026-08-01T02:38:26Z }
sources:
  - id: deepseek-v3-2024
    resource: ../raw/arXiv-2412.19437v2/main.tex
    title: "DeepSeek-V3 Technical Report"
---

# Sequential multi-token prediction

Sequential multi-token prediction (MTP) adds modules that predict several future tokens from each position while retaining a causal chain across depths. DeepSeek-V3 uses one additional depth, sharing embeddings and the output head with the main model; its report presents MTP primarily as an extra training objective, with the modules optionally reused to propose tokens for speculative decoding.[^deepseek-v3-2024]

## Causal-chain modules and loss

At depth $k$, an MTP module combines the preceding-depth representation at position $i$ with the embedding of token $i+k$, projects that pair, and processes it with a depth-specific Transformer block. The shared output head then predicts token $i+k+1$. Unlike independent parallel future-token heads, each depth conditions on the causal chain produced by earlier depths.[^deepseek-v3-2024]

Training adds the mean cross-entropy across $D$ MTP depths, scaled by $\lambda$, to the main objective. In V3, $D=1$: beyond ordinary next-token prediction, the model predicts one additional token. The loss weight is 0.3 for the first 10T tokens and 0.1 for the remaining 4.8T.[^deepseek-v3-2024]

## Inference roles and limits

The main model can discard MTP modules and run normally, so their training-time capacity need not be deployed for ordinary decoding. When repurposed for speculative decoding, however, their proposals still require target-model verification to preserve target-model sampling behavior; MTP is a proposal mechanism, not a replacement for verification.[^deepseek-v3-2024]

In matched small and large MoE ablations, V3’s MTP variants improve most listed benchmark scores but not every score. The report also states an 85–90% second-token acceptance rate across its tested generation topics and 1.8× tokens/s with speculative decoding. Those deployment results do not identify the request mix, batch size, or implementation conditions required to reproduce them.[^deepseek-v3-2024]

## Relationships

- **Used by:** [DeepSeek-V3 architecture and pretraining](deepseek-v3-architecture-and-pretraining.md) as a one-depth objective.
- **Can operationalize:** [Speculative decoding exact sampling](speculative-decoding-exact-sampling.md) after target verification.
- **Qualified by:** [Speculative decoding performance trade-offs](speculative-decoding-performance-trade-offs.md), where draft cost, acceptance, verification, and serving overhead determine realized speedup.

## Evidence limits

This is primary evidence for the V3 implementation and its controlled ablations, but not evidence that sequential MTP is universally better than parallel heads or other draft designs. The stated quality and speed claims are author-run results under undisclosed full system and workload details.[^deepseek-v3-2024]

[^deepseek-v3-2024]: DeepSeek-AI, “DeepSeek-V3 Technical Report,” arXiv:2412.19437v2, [source](../raw/arXiv-2412.19437v2/main.tex), Sections 2.2, 5.3, 6.3, and Table 4.
