---
type: Concept
title: N-gram embedding scaling versus MoE expert scaling
description: In a LongCat-Flash-controlled study, hashed N-gram embedding capacity outperformed matched expert scaling only after the base MoE entered a high-sparsity regime, with allocation and architecture-dependent limits.
tags: [embeddings, n-gram-embeddings, mixture-of-experts, scaling, sparse-models]
status: stable
created: 2026-08-25
generated: { by: llm-wiki-agent/1, at: 2026-08-25T16:09:50Z }
sources:
  - id: longcat-embedding-scaling-2026
    resource: ../raw/2601.21204_ScalingEmbeddingsOutperformsScalingExpertsinLanguageModels/longcat.tex
    title: "Scaling Embeddings Outperforms Scaling Experts in Language Models"
---

# N-gram embedding scaling versus MoE expert scaling

In an author-run LongCat-Flash study with matched total-parameter MoE baselines, allocating capacity to hashed N-gram embeddings lowered reported loss more effectively than adding experts only once the base MoE had reached a high-sparsity regime. The reported frontier is conditional on the tested architecture, 280M/790M/1.3B activated-parameter budgets, and 300B-token pre-training; it is not a general rule that embedding parameters are better than experts.[^longcat-embedding-scaling-2026]

## Compared capacity axes

The study augments a base token embedding with tables addressed by suffix n-grams. Its final form splits each n-gram table into $K$ hash-addressed sub-tables and projects their outputs to the model width before averaging them with the base embedding. Holding sub-table width inversely proportional to $(N-1)K$ keeps the N-gram-embedding parameter count invariant as maximum order $N$ and sub-table count $K$ change.[^longcat-embedding-scaling-2026]

For each N-gram configuration, the comparison baseline matches total parameters by adding MoE experts. This isolates a reported allocation choice—sparse local lookup versus more conditional FFN capacity—rather than a comparison of arbitrary model sizes.[^longcat-embedding-scaling-2026]

## Reported allocation and architecture effects

- At low total-to-activated parameter ratios, adding experts was more effective in the reported loss curves. N-gram embeddings became advantageous after the base MoE exceeded a reported expert-scaling “sweet spot.”[^longcat-embedding-scaling-2026]
- The reported N-gram advantage declined when too much of the parameter budget went to the lookup tables. In the examined 280M-active setting, the crossover was slightly above a total-to-active ratio of 20, where N-gram tables were about half of total parameters; the authors therefore recommend no more than 50% as a configuration-specific guideline.[^longcat-embedding-scaling-2026]
- With fixed depth, wider 790M- and 1.3B-active models retained the reported advantage to higher ratios than the 280M model. At a roughly 50% N-gram allocation, the advantage contracted materially beyond 20 layers in the reported depth sweep.[^longcat-embedding-scaling-2026]

## Lookup and training design findings

The source reports collision spikes for its polynomial rolling 2-gram hash when table vocabulary sizes approach integer multiples of the base vocabulary. It recommends choosing table sizes substantially away from such multiples; this is an observation about that addressing scheme, not a universal property of hashing.[^longcat-embedding-scaling-2026]

The weakest ablation was $N=2, K=1$; for the tested 790M-active configuration, $N\geq3$ and $K\geq2$ had relatively small differences, with orders 3–5 near the reported optimum. The authors also report that scaling the embedding output (typically by $\sqrt D$) or normalizing it before its residual merge counteracted early-layer signal domination and reduced their reported training and validation losses by about 0.02 relative to their unadjusted N-gram setup.[^longcat-embedding-scaling-2026]

A per-layer variant injects layer-specific N-gram embeddings into the SwiGLU path. It slightly improved the reported matched N-gram baseline at one setting, but did not consistently retain an advantage as width or depth grew and increased activated parameters through per-layer projections.[^longcat-embedding-scaling-2026]

## Evidence limits

All scaling curves, collision measurements, and loss results are author-run experiments on the LongCat-Flash architecture. The report does not provide training code, data composition, checkpoints, full hyperparameter/configuration files, independent replications, or a cross-architecture study; its allocation thresholds and comparative claims should therefore be treated as source-specific evidence.[^longcat-embedding-scaling-2026]

## Relationships

- **Specific empirical study of:** [N-gram embeddings and conditional memory](n-gram-embeddings-and-conditional-memory.md).
- **Compares against:** [Mixture-of-Experts training and systems trade-offs](mixture-of-experts-training-and-systems-trade-offs.md); its matched baseline changes expert count, not the general MoE design space.
- **Architecture realization in:** [LongCat-Flash-Lite N-gram-embedding architecture](longcat-flash-lite-ngram-embedding-architecture.md).
- **Evaluation and serving evidence in:** [LongCat-Flash-Lite evaluation, deployment, and release limits](longcat-flash-lite-evaluation-deployment-and-release-limits.md).

[^longcat-embedding-scaling-2026]: Hong Liu et al. (Meituan LongCat Team), “Scaling Embeddings Outperforms Scaling Experts in Language Models,” [LaTeX source](../raw/2601.21204_ScalingEmbeddingsOutperformsScalingExpertsinLanguageModels/longcat.tex), Abstract and Sections 2–6. Figure attachments were visually inspected.