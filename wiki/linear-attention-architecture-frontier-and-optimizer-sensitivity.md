---
type: Concept
title: Linear-attention architecture frontier and optimizer sensitivity
description: A 350M/15B-token author-run sweep places Kimi Delta Attention/Muon at the lowest reported loss and pure Gated DeltaNet/AdamW at the highest normalized training throughput, with learning-rate and hybrid-stack choices materially changing the frontier.
tags: [deltanet, evaluation, hybrid-attention, linear-attention, muon, throughput]
status: stable
created: 2026-08-24
generated: { by: llm-wiki-agent/1, at: 2026-08-24T02:22:56Z }
sources:
  - id: linear-attention-architectures-2026
    resource: ../raw/2607.07953_LinearAttentionArchitectures/template.tex
    title: "Linear Attention Architectures: Mechanisms, Trade-offs, and Cross-Layer Routing"
---

# Linear-attention architecture frontier and optimizer sensitivity

A supplied author-run comparison of 350M-class models trained for 15B tokens finds no single winner: Kimi Delta Attention (KDA) with Muon and a hybrid stack has the lowest reported final validation loss (2.273), while a pure Gated DeltaNet stack with AdamW has the reference-best normalized training throughput (100%) but higher final loss (2.433). The result is a configuration-bound loss/throughput frontier, not a general ranking or an inference benchmark.[^linear-attention-architectures-2026]

## Scope and comparison boundary

The main sweep uses decoder-only models trained on FineWeb-Edu with a LLaMA 2 tokenizer, 4,096-token sequences, global batch 128, bf16, and one four-GPU GH200 node. It holds those data and systems choices fixed while varying the mixer, optimizer, and pure versus hybrid stack; architecture-specific depths vary to keep recorded parameter counts near 350M. Every reported architecture row is a single run, so there are no standard deviations.[^linear-attention-architectures-2026]

A hybrid stack interleaves recurrent linear-memory layers with softmax-attention layers, normally one softmax layer in every three. A pure stack uses its recurrent mixer throughout. Thus hybrid results also test restored token-addressable attention; they do not isolate the recurrent update alone.[^linear-attention-architectures-2026]

## Reported frontier

The 15B-token table compares softmax attention, DeltaNet, Gated DeltaNet, KDA, and Gated DeltaNet-2 (GDN2) under AdamW and Muon. Its selected endpoints are:

| Configuration | Final validation loss | Relative training throughput |
| --- | ---: | ---: |
| KDA, Muon, hybrid | 2.273 | 70.9% |
| DeltaNet, Muon, hybrid | 2.299 | 83.8% |
| Gated DeltaNet, Muon, hybrid | 2.321 | 89.5% |
| Softmax, Muon | 2.349 | 79.7% |
| Gated DeltaNet, AdamW, pure | 2.433 | 100.0% |

Within each architecture/stack pair shown, Muon has lower final loss than AdamW. Hybrid variants also have lower loss than their pure counterparts in this table, but retain some softmax cost. These patterns are empirical observations in the stated sweep, not proof that either optimizer or hybridization universally dominates.[^linear-attention-architectures-2026]

## Learning-rate and length sensitivity

A separate 2,000-step (about 1.05B-token) hybrid ablation shows that the preferred learning rate depends on the optimizer and mixer. The report places Muon's useful region near $3\times10^{-4}$, whereas its AdamW linear-attention runs prefer about $10^{-3}$; a single optimizer-independent default can therefore confound an architecture comparison.[^linear-attention-architectures-2026]

The timing study measures *training iteration time*, not decoding speed. At 32K tokens, the reported times are 3.37 s for softmax, 1.56 s for hybrid Gated DeltaNet, and 0.96 s for pure Gated DeltaNet. From 4K to 32K, they grow about 2.9x, 1.7x, and 1.1x, respectively. This demonstrates the expected sequence-length scaling advantage of the recurrent stacks under this kernel and hardware configuration, while quantifying the hybrid trade-off.[^linear-attention-architectures-2026]

## Interpretation limits

- The normalized speed denominator is pure Gated DeltaNet/AdamW in this 350M/15B sweep. It is neither an absolute throughput nor an inference-latency metric.[^linear-attention-architectures-2026]
- Larger DeltaNet-only runs and HellaSwag, PIQA, and WinoGrande checks are supplementary context, not a complete cross-architecture or repeated-seed study.[^linear-attention-architectures-2026]
- The source itself cautions that small loss gaps, especially around $10^{-3}$ to $10^{-2}$, are not robust without matched settings, repeated runs, or corroborating evidence.[^linear-attention-architectures-2026]

## Relationships

- **Compares:** [DeltaNet evaluation and hybrid-attention trade-offs](deltanet-evaluation-and-hybrid-attention-trade-offs.md), [Gated DeltaNet evaluation and hybrid trade-offs](gated-deltanet-evaluation-and-hybrid-trade-offs.md), and [Gated DeltaNet-2 evaluation and hybrid trade-offs](gated-deltanet-2-evaluation-and-hybrid-trade-offs.md) under a distinct 350M/15B recipe.
- **Evaluates mechanisms in:** [Delta-rule and gated associative memory](delta-rule-and-gated-associative-memory.md).
- **Uses:** [Muon orthogonalized-momentum optimizer](muon-orthogonalized-momentum-optimizer.md) as one of the compared optimizers.
- **Introduces and evaluates:** [Cross-layer value routing for delta memories](cross-layer-value-routing-for-delta-memories.md).

[^linear-attention-architectures-2026]: Tommaso Cerruti, Tim Rieder, George Rowlands, Lingfeng Jin, and Imanol Schlag, “Linear Attention Architectures: Mechanisms, Trade-offs, and Cross-Layer Routing,” supplied LaTeX source, [source](../raw/2607.07953_LinearAttentionArchitectures/template.tex), Abstract; Sections 4–7; Tables 1–6; and Appendix A–B.