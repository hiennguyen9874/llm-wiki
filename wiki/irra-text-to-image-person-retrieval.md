---
type: Concept
title: IRRA for text-to-image person retrieval
description: IRRA combines CLIP dual encoders, masked-language cross-modal relation reasoning, and similarity-distribution matching for efficient global person retrieval.
tags: [cross-modal-retrieval, clip, masked-language-modeling, person-reidentification]
status: stable
created: 2026-09-16
generated: { by: llm-wiki-agent/1, at: 2026-09-16T08:01:59Z }
sources:
  - id: arxiv-2303.12501
    resource: ../raw/papers/arxiv-2303.12501/PaperForReview.tex
    title: Cross-Modal Implicit Relation Reasoning and Aligning for Text-to-Image Person Retrieval
---

# IRRA for text-to-image person retrieval

IRRA is a text-to-image person-retrieval framework that fine-tunes CLIP's full image and text encoders while using fine-grained cross-modal interaction only as training supervision. Its core design combines global dual-encoder retrieval with masked-language implicit relation reasoning (IRR), bidirectional similarity distribution matching (SDM), and identity classification. The interaction-only modules are removed at inference, so retrieval requires one global image-text similarity score rather than explicit local-part matching.[^arxiv-2303.12501]

## Architecture and training

- A CLIP ViT image encoder and CLIP Transformer text encoder produce global embeddings in a shared space.
- **IRR branch:** 15% of text tokens are selected using BERT-style replacement proportions (80% mask, 10% random, 10% unchanged). Masked text states query image states through multi-head cross-attention, followed by four Transformer layers and token prediction. This masked-language objective forces contextual text-image representations to recover local textual details.[^arxiv-2303.12501]
- **SDM branch:** within a minibatch, temperature-scaled cosine similarities define image-to-text and text-to-image distributions. The stated loss minimizes KL divergence from each predicted similarity distribution to the normalized same-identity label distribution in both directions. The temperature is intended to control distribution sharpness and emphasize hard negatives.[^arxiv-2303.12501]
- **Identity branch:** image and text embeddings are classified by person identity to cluster same-identity representations.
- The total objective is unweighted in the manuscript: $\mathcal{L}=\mathcal{L}_{irr}+\mathcal{L}_{sdm}+\mathcal{L}_{id}$.[^arxiv-2303.12501]

**Synthesis:** the design uses an expensive cross-encoder-like interaction path as a training-time teacher signal for efficient dual-encoder inference. It therefore aims to retain global embedding retrieval speed while injecting token-level grounding into the encoders.

## Reported evidence

Using CLIP-ViT-B/16, the paper reports the following test results:[^arxiv-2303.12501]

| Dataset | Rank-1 | Rank-5 | Rank-10 | mAP | mINP |
|---|---:|---:|---:|---:|---:|
| CUHK-PEDES | 73.38 | 89.93 | 93.71 | 66.13 | 50.24 |
| ICFG-PEDES | 63.46 | 80.25 | 85.82 | 38.06 | 7.93 |
| RSTPReid | 60.20 | 81.30 | 88.20 | 47.17 | 25.28 |

The component ablation reports that adding IRR to the InfoNCE-fine-tuned CLIP baseline raises Rank-1 by 3.04, 4.22, and 3.85 percentage points on CUHK-PEDES, ICFG-PEDES, and RSTPReid respectively. Replacing InfoNCE with SDM raises Rank-1 by 2.23, 3.71, and 3.15 points. Under the full IRRA setting, the proposed multimodal interaction module is reported at 13.66M parameters and 6.42 ms, compared with 33.62M/24.30 ms for co-attention and 12.61M/19.20 ms for merged attention; the manuscript does not fully specify the timing protocol.[^arxiv-2303.12501]

These results are author-reported comparisons, not independently reproduced here. The paper evaluates on three person-retrieval benchmarks but does not establish transfer to general image-text retrieval or later model families.

## Implementation details

The reported setup resizes images to $384\times128$, limits text to 77 tokens, trains for 60 epochs with Adam and cosine decay, uses five warm-up epochs, and sets the SDM temperature to 0.02. Pretrained modules start at a $10^{-5}$ learning rate and randomly initialized modules at $5\times10^{-5}$. Experiments were run on one RTX 3090 24 GB GPU; the authors provide an implementation link at <https://github.com/anosorae/IRRA>.[^arxiv-2303.12501]

## Limitations and source inconsistencies

The authors observe that random single-token masking captures word-level semantics but can miss phrase-level meaning; they propose phrase-level masking as future work. They also note relatively low mINP on ICFG-PEDES, indicating weakness on the hardest matching samples.[^arxiv-2303.12501]

Two numerical inconsistencies in the manuscript should be resolved against released code or official result tables before exact reuse:

- The CUHK-PEDES prose says the CLIP-ViT-B/16 baseline reaches “Rank-1 accuracy and mAP” of 68.19 and 86.47, but Table 1 assigns 86.47 to Rank-5 and reports mAP as 61.12.
- Table 1 reports IRRA Rank-5 on CUHK-PEDES as 89.93, while the component ablation table reports 89.83 for the full system.

[^arxiv-2303.12501]: Ding Jiang and Mang Ye, “Cross-Modal Implicit Relation Reasoning and Aligning for Text-to-Image Person Retrieval,” CVPR 2023 manuscript, [`PaperForReview.tex`](../raw/papers/arxiv-2303.12501/PaperForReview.tex). Architecture and qualitative retrieval figures in the same source bundle were also visually inspected.
