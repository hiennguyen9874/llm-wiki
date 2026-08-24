---
type: Concept
title: Hyena hierarchy evaluation and trade-offs
description: The Hyena draft reports competitive small-scale language and long-recall results, with performance and speed claims limited by author-run, configuration-specific evidence and an internal runtime discrepancy.
tags: [hyena, evaluation, efficiency, long-context, convolution]
status: stable
created: 2026-08-24
generated: { by: llm-wiki-agent/1, at: 2026-08-24T00:00:00Z }
sources:
  - id: poli-etal-2023
    resource: ../raw/2302.10866_HyenaHierarchy/main.tex
    title: "Hyena Hierarchy: Towards Larger Convolutional Language Models"
---

# Hyena hierarchy evaluation and trade-offs

The Hyena draft reports that its attention-free convolutional models match selected small GPT baselines on language modeling and solve its difficult associative-recall setup at lengths where listed alternatives fail. The evidence is author-run, below billion-scale for the central language comparisons, and depends on training, kernel, and hardware configurations; its embedded runtime data also conflicts with its stated 100× FlashAttention claim.[^poli-etal-2023]

## Reported language and recall results

- On WikiText-103, the reported 125M-parameter Hyena-3 has 18.6 perplexity (18.5 for the deeper “slim” variant), versus 18.6 for the listed 125M Transformer under the same tokenizer.[^poli-etal-2023]
- On The Pile after 15B training tokens, the 355M Hyena-2 reports 9.2 perplexity at $3.93\times10^{19}$ FLOPs, versus the listed 355M GPT’s 9.1 at $4.77\times10^{19}$ FLOPs. This is a configuration-specific compute–quality comparison, not a same-parameter or exact-quality win.[^poli-etal-2023]
- In the paper’s two-layer, width-64 associative-recall task (vocabulary 30), Hyena reports 100.0%, 100.0%, and 97.2% at 30K, 64K, and 131K tokens. The listed FlashTransformer reports 32.4% and 26.7% at 30K and 64K and does not fit at 131K; the paper notes its fixed 2,000-example training regime makes Transformers struggle. This is synthetic-task evidence, not general in-context-learning parity.[^poli-etal-2023]
- The source also reports matched ImageNet-1K top-1 accuracy for 88M Hyena-ViT and 87M ViT at 16×16 patches (78.5%), and 79.8% versus 80.0% at 8×8 patches.[^poli-etal-2023]

## Runtime and deployment boundary

The runtime benchmark uses an order-2 Hyena with fused FFT convolution, batch size 64, and compares operator runtime with attention and FlashAttention. Its text says the Hyena–attention crossover is 2,048 tokens and the Hyena–FlashAttention crossover lies between 4,096 and 8,192; the included plot data supports these local crossovers. At 8,192 tokens it plots 1.50 ms for Hyena and 2.10 ms for FlashAttention.[^poli-etal-2023]

FFT-heavy long convolution has lower accelerator utilization than FlashAttention in the source’s account, so a FLOP reduction becomes a measured speedup only at longer sequences. End-to-end deployment still depends on projection/MLP work, prefill versus decode, FFT kernels, sequence length, batch size, precision, and accelerator; the report does not establish a universal serving advantage.[^poli-etal-2023]

## Contradictions

- **100× claim versus embedded data:** The abstract and experiment prose claim a 100× Hyena speedup over FlashAttention at 64K tokens. The bundled plotting source for that benchmark instead gives 11.32 ms (Hyena) and 129.07 ms (FlashAttention) at 65,536 tokens—about 11.4×. The source does not explain the discrepancy, so the 100× figure should not be relied on without an erratum or independently reproducible benchmark.[^poli-etal-2023]

## Relationships

- **Evaluates:** [Hyena hierarchy architecture](hyena-hierarchy-architecture.md).
- **Contrasts with:** [Self-attention computational profile](self-attention-computational-profile.md): Hyena’s operator benchmark does not remove attention’s direct token-addressable paths or demonstrate speed at all lengths.
- **Contrasts with:** [Mamba evaluation and implementation trade-offs](mamba-evaluation-and-implementation-trade-offs.md): both report subquadratic alternatives under narrow configurations, but Hyena uses input-controlled convolutions and FFTs rather than a selective recurrent scan.

## Evidence limits

All measurements are reported by the paper’s authors, with no independent replication in the supplied source. Comparisons vary in parameter count, training tokens, architecture, and implementation, so they support only the stated experiments. The draft’s runtime contradiction and its limited large-scale evidence make its broader replacement claims uncertain.[^poli-etal-2023]

[^poli-etal-2023]: Michael Poli et al., “Hyena Hierarchy: Towards Larger Convolutional Language Models,” arXiv:2302.10866, bundled [LaTeX source](../raw/2302.10866_HyenaHierarchy/main.tex), Sections 4–5 and Appendices A/C; runtime values are in [the included benchmark plot source](../raw/2302.10866_HyenaHierarchy/figures/source/bench.tex).
