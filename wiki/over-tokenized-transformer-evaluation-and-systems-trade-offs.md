---
type: Concept
title: Over-tokenized Transformer evaluation and systems trade-offs
description: Author-run OLMo/OLMoE experiments report that Over-Encoding lowers loss and can complement sequential multi-token prediction, while large sparse tables introduce memory and distributed-communication overhead.
tags: [evaluation, embeddings, n-grams, scaling-laws, multi-token-prediction, systems]
status: stable
created: 2026-08-25
generated: { by: llm-wiki-agent/1, at: 2026-08-25T15:25:18Z }
sources:
  - id: over-tokenized-transformer-2025
    resource: ../raw/2501.16975_Over-TokenizedTransformer/main.tex
    title: "Over-Tokenized Transformer: Vocabulary is Generally Worth Scaling"
---

# Over-tokenized Transformer evaluation and systems trade-offs

In author-run OLMo2 and OLMoE experiments, Over-Encoding (OE) reports lower held-out loss than its selected baselines and, in one small-MoE experiment, a higher aggregate downstream score when combined with DeepSeek-style sequential multi-token prediction (MTP-DS). The source’s “no additional cost” framing applies to added dense arithmetic, not to total model storage or realized communication overhead.[^over-tokenized-transformer-2025]

## Reported quality and vocabulary scaling

- At 400B training tokens, the source reports an OE-12.8M 400M dense OLMo2 model matching the training loss of its 1B baseline. For the 1B pair trained to 1T tokens, it reports a 0.14 loss improvement and convergence-acceleration ratios from 2.6× to 5.7× across loss and five downstream measures.[^over-tokenized-transformer-2025]
- For OLMoE models trained on 500B tokens, OE-12.8M changes loss from 2.554 to 2.472 and the five-task aggregate from 0.510 to 0.524 at 1.3B total parameters; at 7B total parameters, the corresponding reported values are 2.305 to 2.229 and 0.601 to 0.608.[^over-tokenized-transformer-2025]
- In a 1.3B OLMoE vocabulary ablation with a 2-gram table, the authors fit $\mathcal{L}=2.6754-0.0256\log_{10}m$ after 500B tokens, where $m$ is the additional table’s row count. Larger tables also converged more slowly in their curves. This is a fitted result for that model, tokenizer, data, optimizer, and training budget—not a general scaling law.[^over-tokenized-transformer-2025]

## Combined future-token objective

At the authors’ 1.3B OLMoE setting, MTP and MTP-DS alone did not improve the listed next-token loss; MTP-DS changed the aggregate downstream score only from 0.510 to 0.511. OE-12.8M reached 2.472 training loss, 2.862 evaluation loss, and 0.524 aggregate score. Combining OE with MTP-DS (OT-12.8M) worsened those losses to 2.481 and 2.869 but raised the aggregate to 0.537. This supports complementarity in that setting, not a claim that the combination uniformly improves loss or transfers to other model scales.[^over-tokenized-transformer-2025]

The source also reports a separate Over-Decoding objective that predicts future base tokens through factorized output heads. In its 1.3B and 7B OLMoE runs, the objective lagged early and only exceeded baseline next-token loss after more than 200B tokens; its downstream changes varied with future-loss weight. This is related to, but architecturally distinct from, OE’s input lookup capacity.[^over-tokenized-transformer-2025]

## Systems accounting

A 12.8M-row OE table is sparse per token but large in memory. The paper proposes row-sharding it across data-parallel ranks: route lookup IDs to the owning rank, return vectors, and use two forward plus one backward all-to-all operations. It reports that this reduced the FSDP throughput penalty to under 5% at $m=10^7$, compared with a stated 25% slowdown without that approach; the pipeline overlap and CPU-offload options are proposals, not evaluated end-to-end results.[^over-tokenized-transformer-2025]

In separately reported OLMoE training measurements, OE-12.8M throughput was 4.63% lower on 32 A100s for OLMoE-1.3B and 8.3% lower on 64 A100s for OLMoE-7B. Its calculated forward FLOPs per token rose by about 0.35–0.38%. On one A100 using `transformers`, the authors CPU-offloaded added embeddings and report near-baseline prefill/decode throughput under their fixed 2,048-token workloads; CPU memory, transfer, and production serving behavior remain unreported.[^over-tokenized-transformer-2025]

## Evidence limits

All numerical results are author-run and the source does not provide full reproducibility artifacts, variance, or an independent evaluation. The comparisons retain each baseline tokenizer, but model sizes, corpus/training details, hardware, and communication implementations bound cross-model interpretation. Loss/perplexity should not be compared across tokenizers without a common unit and evaluation protocol.

## Relationships

- **Evaluates:** [Over-Encoding hierarchical n-gram input embeddings](over-encoding-hierarchical-n-gram-input-embeddings.md).
- **Combines with:** [Sequential multi-token prediction](sequential-multi-token-prediction.md) in the paper’s OT experiment.
- **Qualifies:** [Empirical language-model loss scaling laws](empirical-language-model-loss-scaling-laws.md): the reported log-linear vocabulary fit changes the input-embedding design and is not evidence that Kaplan-style laws have been replaced.
- **Related sparse-capacity mechanism:** [Mixture-of-Experts training and systems trade-offs](mixture-of-experts-training-and-systems-trade-offs.md); both distinguish total stored parameters from per-token dense work, but OE’s lookup routing has different bottlenecks.

[^over-tokenized-transformer-2025]: Hongzhi Huang et al., “Over-Tokenized Transformer: Vocabulary is Generally Worth Scaling,” ICML 2025, [LaTeX source](../raw/2501.16975_Over-TokenizedTransformer/main.tex), Sections 3–4 and Appendix “OLMoE Experiments” and “Over-Decoding.”
