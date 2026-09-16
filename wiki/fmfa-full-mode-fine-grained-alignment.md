---
type: Concept
title: FMFA full-mode fine-grained person retrieval
description: FMFA augments IRRA with adaptive positive-pair weighting and sparse explicit token-patch alignment during training while retaining global-only text-to-image person retrieval at inference.
tags: [cross-modal-retrieval, clip, fine-grained-alignment, person-reidentification]
status: stable
created: 2026-09-16
generated: { by: llm-wiki-agent/1, at: 2026-09-16T08:16:49Z }
sources:
  - id: arxiv-2509.13754v2
    resource: ../raw/papers/arXiv-2509.13754v2/sample-acmsmall.tex
    title: Cross-modal Full-mode Fine-grained Alignment for Text-to-Image Person Retrieval
---

# FMFA full-mode fine-grained person retrieval

FMFA (Full-Mode Fine-grained Alignment) extends IRRA's CLIP dual-encoder framework with two training-only objectives: Adaptive Similarity Distribution Matching (A-SDM), which upweights a true image-text pair when it is not the batch's top-scoring match, and Explicit Fine-grained Alignment (EFA), which constructs token-conditioned visual embeddings from a sparse token-patch similarity matrix. FMFA retains IRRA's identity and masked-language implicit-relation objectives. All interaction modules are removed at inference, leaving global image and text embeddings for efficient retrieval.[^arxiv-2509.13754v2]

## Architecture and objectives

- **Backbone and inherited objectives:** CLIP ViT-B/16 and CLIP Transformer encoders produce global and local visual/text features. Identity classification provides coarse global supervision, while IRRA's masked-language Implicit Relation Reasoning (IRR) provides attention-based local supervision.[^arxiv-2509.13754v2]
- **A-SDM:** bidirectional, temperature-scaled similarity-distribution matching is multiplied by an adaptive per-query weight. For text-to-image matching, the weight is $1+\alpha(\max_k p_{i,k}-p_{i,i})$. It remains 1 when the true pair is top-ranked and grows with the gap when another batch image ranks above it. Thus “unmatched positive” means a labeled positive that the current model does not rank first, not an incorrect ground-truth pair.[^arxiv-2509.13754v2]
- **EFA sparse aggregation:** token-patch inner products are min-max normalized per token and values below $\sigma=1/N$ are zeroed. The surviving patch features are normalized and aggregated into one language-grouped visual embedding per token.[^arxiv-2509.13754v2]
- **EFA hard alignment:** for each local embedding, only its maximum cosine match is retained; log-sum-exp pooling forms image-to-joint and text-to-joint similarities. A bidirectional soft-margin triplet-style loss aligns the joint embeddings with their originating image and text features.[^arxiv-2509.13754v2]
- The manuscript gives the unweighted objective $\mathcal{L}=\mathcal{L}_{id}+\mathcal{L}_{irr}+\mathcal{L}_{efa}+\mathcal{L}_{A\text{-}sdm}$. EFA, IRR, and the loss heads are training-only, so the added fine-grained interaction does not change the dual-encoder inference path.[^arxiv-2509.13754v2]

**Synthesis:** A-SDM and EFA target different errors. A-SDM operates on global rankings and increases pressure on labeled positives that trail an in-batch negative; EFA supplies explicit local correspondence supervision that IRR's latent attention does not expose. The resulting local machinery acts as training-time representation shaping rather than an inference-time reranker.

## Reported evidence

With ordinary CLIP initialization, the paper reports:[^arxiv-2509.13754v2]

| Dataset | Rank-1 | Rank-5 | Rank-10 | mAP |
|---|---:|---:|---:|---:|
| CUHK-PEDES | 74.16 | 90.12 | 94.10 | 66.66 |
| ICFG-PEDES | 64.29 | 80.48 | 85.93 | 39.43 |
| RSTPReid | 61.05 | 83.85 | 89.80 | 48.22 |

Against the authors' IRRA reimplementation, FMFA improves Rank-1 by 0.71, 0.81, and 1.55 percentage points on CUHK-PEDES, ICFG-PEDES, and RSTPReid respectively. The reported mAP gains are 0.53, 1.23, and 0.78 points. With HAM ReID-domain pretraining, FMFA reaches 77.46/68.89 Rank-1/mAP on CUHK-PEDES, 68.37/41.76 on ICFG-PEDES, and 71.80/55.72 on RSTPReid; the gains over HAM plus the reproduced IRRA are only 0.14-0.45 Rank-1 points.[^arxiv-2509.13754v2]

The component ablation supports both additions but shows small and metric-dependent effects. Relative to the SDM baseline, A-SDM alone raises Rank-1 by 0.59, 0.78, and 0.75 points across the three datasets; EFA alone raises it by 0.28, 0.29, and 0.95 points. Combining them gives the strongest Rank-1 result in each ablation, although EFA lowers ICFG-PEDES Rank-5 by 0.11 when added to A-SDM. The authors attribute this exception to information discarded by sparse hard selection.[^arxiv-2509.13754v2]

Reported whole-test-set inference times are 3/7/50 seconds on RSTPReid/CUHK-PEDES/ICFG-PEDES, versus 5/16/91 for PLOT and 388/1168/3871 for RaSa. The paper attributes this advantage to global-only inference. These are author-reported system measurements; the manuscript lists an RTX A6000 but does not provide enough per-method implementation and timing protocol detail for hardware-independent comparison.[^arxiv-2509.13754v2]

## Implementation details

The default setup resizes images to $384\times128$, caps text at 77 tokens, and trains with Adam and cosine learning-rate decay for 60 epochs (100 on ICFG-PEDES), batch size 64, and a $10^{-5}$ initial learning rate for original CLIP. A-SDM uses temperature $\tau_1=0.02$ and $\alpha=10$, except $\alpha=1$ on RSTPReid. EFA uses $\tau_2=1$, sparsity threshold $\sigma=1/N$, and log-sum-exp factor $\lambda=1$; triplet margins vary by dataset and direction. The paper links code at <https://github.com/yinhao1102/FMFA>.[^arxiv-2509.13754v2]

The parameter study reports that both proposed loss weights work best at 1. Setting the EFA weight to 5 or 10 causes training collapse, with all reported CUHK-PEDES retrieval metrics below 1. Removing the constant $+1$ from A-SDM reduces CUHK-PEDES Rank-1 from 74.16 to 26.12, consistent with eliminating gradients from already top-ranked positives.[^arxiv-2509.13754v2]

## Limitations and source ambiguities

- The fixed EFA threshold can discard informative patches. The authors identify semantic information loss as the main limitation and suggest adaptive aggregation as future work.[^arxiv-2509.13754v2]
- Evidence is limited to three person-retrieval datasets and is not independently reproduced here. The paper's “best global method” claim is bounded by its selected comparators, model versions, and metrics.
- Gains over the reproduced IRRA baseline are generally modest and become especially small with ReID-domain pretrained backbones. No variance across random seeds or significance test is reported.[^arxiv-2509.13754v2]
- The A-SDM ground-truth distribution equation writes $q_{i,j}=y_{i,j}/\sum_{k=1}^{B}$ without a summand, and the EFA aggregation denominator retains $j$ while summing over $m$. Both appear typographically incomplete and should be checked against the released implementation before reimplementation.[^arxiv-2509.13754v2]
- The appendix's hard-coding complexity discussion states $\mathcal{O}(N)$ processing after forming an $N\times L$ similarity matrix and contrasts $\mathcal{O}(NL)$ hard-coding storage with $\mathcal{O}(Ld)$ soft-coding storage. The accounting is underspecified and should not be reused as a general complexity result without code-level verification.[^arxiv-2509.13754v2]

## Relationships

- **Builds on:** [IRRA for text-to-image person retrieval](irra-text-to-image-person-retrieval.md) supplies the CLIP encoders, identity loss, IRR branch, and SDM baseline that A-SDM replaces.[^arxiv-2509.13754v2]
- **Compared with:** [MARS attribute-aware text-based person search](mars-attribute-aware-person-search.md) also learns fine-grained correspondences, but MARS reranks candidates with a cross-modal encoder at inference while FMFA removes local interaction modules.
- **Compared with:** [TBPS-CLIP empirical person-search baseline](tbps-clip-empirical-person-search-baseline.md) is a simpler global CLIP fine-tuning approach without FMFA's explicit token-patch training objective.

[^arxiv-2509.13754v2]: Hao Yin, Xin Man, Feiyu Chen, Jie Shao, and Heng Tao Shen, “Cross-modal Full-mode Fine-grained Alignment for Text-to-Image Person Retrieval,” arXiv:2509.13754v2 / ACM TOMM manuscript, 2025, [`sample-acmsmall.tex`](../raw/papers/arXiv-2509.13754v2/sample-acmsmall.tex). The architecture, A-SDM, EFA, and sparse-similarity figures in the same source bundle were also visually inspected.
