---
type: Concept
title: GQA checkpoint conversion and uptraining
description: A pretrained MHA checkpoint can be converted to GQA by averaging grouped K/V projections and then continuing pretraining, providing a reported lower-cost migration path rather than a guarantee of parity with training from scratch.
tags: [attention, grouped-query-attention, uptraining, checkpoint-conversion, inference]
status: draft
created: 2026-07-31
generated: { by: llm-wiki-agent/1, at: 2026-07-31T16:47:41Z }
sources:
  - id: gqa-summary
    resource: ../raw/GQA.md
    title: "GQA overview (Vietnamese summary)"
---

# GQA checkpoint conversion and uptraining

A pretrained multi-head-attention (MHA) model can be migrated to grouped-query attention (GQA) without pretraining anew: for every target KV group, average the original MHA key and value projection weights in that group, retain query and output projections, then continue pretraining so the model adapts to shared K/V representations. The paper reports this as an effective initialization and limited-compute procedure in its T5 experiments, not as proof that converted GQA matches a from-scratch GQA model.[^gqa-summary]

## Conversion

For source MHA K/V projection matrices in target group $\mathcal{G}_j$, initialize each GQA K/V projection by mean pooling:

$$
W_j^{K,\mathrm{GQA}}=\frac{1}{|\mathcal{G}_j|}\sum_{i\in\mathcal{G}_j}W_i^{K,\mathrm{MHA}},
\qquad
W_j^{V,\mathrm{GQA}}=\frac{1}{|\mathcal{G}_j|}\sum_{i\in\mathcal{G}_j}W_i^{V,\mathrm{MHA}}.
$$

The source reports mean pooling outperforming selecting the first head or random initialization in the tested conversion. It attributes this advantage to preserving more of the original checkpoint’s information.[^gqa-summary]

## Continued pretraining and scope

The converted model requires continued pretraining ("uptraining") with the original pretraining recipe and data. In the main T5-XXL experiments, the reported uptraining fraction was $\alpha=0.05$, about 5% of original pretraining compute; moving to 10% had diminishing reported gains. This is a setup-dependent result, and mean pooling alone is not claimed to yield optimal quality.[^gqa-summary]

The paper applies GQA/MQA to decoder self-attention and decoder cross-attention, not encoder self-attention, because autoregressive decode is the relevant KV-cache bandwidth bottleneck. It also notes that multiple KV heads can be distributed across tensor-parallel partitions more naturally than MQA’s sole KV head. Implementations must at least make $H_Q$ divisible by $H_{KV}$; allocating KV heads across tensor-parallel ranks efficiently is an additional deployment constraint.[^gqa-summary]

## Evaluation boundary

The reported experiments are primarily encoder–decoder T5.1.1 models on TPUv4. They do not directly compare an uptrained GQA model with an otherwise equivalent GQA model pretrained from scratch, and their timing depends on workload-specific parallelization. The authors expect decoder-only models to benefit, but that expectation was not directly established by the reported experiments.[^gqa-summary]

## Relationships

- **Converts:** [Multi-query and grouped-query attention](multi-query-and-grouped-query-attention.md) from MHA’s per-head K/V projections to grouped K/V projections.[^gqa-summary]
- **Modifies:** [Scaled dot-product and multi-head attention](scaled-dot-product-and-multi-head-attention.md) only in K/V projection sharing; query and output projections are retained during the described initialization.[^gqa-summary]

[^gqa-summary]: “GQA overview” (Vietnamese summary), [raw source](../raw/GQA.md), Sections 10–18. This is secondary-source evidence summarizing Ainslie et al., “GQA: Training Generalized Multi-Query Transformer Models from Multi-Head Checkpoints” (2023); the primary paper has not been independently ingested here.
